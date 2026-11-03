import json, tempfile, threading, urllib.request, urllib.error, zipfile, io
from pathlib import Path
import store, server
from http.server import ThreadingHTTPServer
with tempfile.TemporaryDirectory() as tmp:
    store.DATA=server.DATA=Path(tmp)
    http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
    threading.Thread(target=http.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{http.server_port}'
    def req(path,data=None,raw=None,headers=None):
        h={'Host':'127.0.0.1:8765','Origin':'http://127.0.0.1:8765','X-Local-Token':server.TOKEN,**(headers or {})}
        if data is not None:raw=json.dumps(data).encode();h['Content-Type']='application/json'
        with urllib.request.urlopen(urllib.request.Request(base+path,data=raw,headers=h),timeout=10) as r:
            body=r.read();return json.loads(body) if 'application/json' in r.headers.get('Content-Type','') else body
    def fails(path,raw=None,headers=None,code=400):
        try:req(path,raw=raw,headers=headers);raise AssertionError('Requête acceptée à tort')
        except urllib.error.HTTPError as e:assert e.code==code,(e.code,e.read())
    assert req('/assets/favicon.png').startswith(b'\x89PNG')
    s=req('/api/start',{'title':'Test récupération','subject':'Finance','language':'fr','source':'online','vocabulary':'acquisition, budget'});sid=s['id'];assert s['source']=='online' and s['vocabulary']=='acquisition, budget';assert s['enrichment_enabled'] and s['research_enabled']
    # Supports are accepted during capture, serialized, deduplicated and removable.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(req,f'/api/support?id={sid}&kind=txt&name=Document{i}&key=upload{i}',raw=('Contenu du support numéro '+str(i)).encode()) for i in range(2)]
        for future in futures:future.result()
    assert len(req('/api/session/'+sid)['supports'])==2
    req(f'/api/support?id={sid}&kind=txt&name=Document0&key=upload0',raw='Contenu du support numéro 0'.encode())
    assert len(req('/api/session/'+sid)['supports'])==2
    before=len(list(store.folder(sid).glob('support-*')))
    fails(f'/api/support?id={sid}&kind=pptx&name=Corrompu',raw=b'not-a-presentation',code=500)
    assert len(list(store.folder(sid).glob('support-*')))==before
    attached=req('/api/session/'+sid)['supports']
    req('/api/support/delete',{'id':sid,'file':attached[0]['file']})
    assert len(req('/api/session/'+sid)['supports'])==1
    # Native Word text and mixed text/blank PDF pages must be handled explicitly.
    word=io.BytesIO()
    with zipfile.ZipFile(word,'w') as archive:
        archive.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Le support Word explique le budget prévisionnel.</w:t></w:r></w:p></w:body></w:document>')
    s=req(f'/api/support?id={sid}&kind=docx&name=Support.docx',raw=word.getvalue())
    assert 'budget prévisionnel' in s['supports'][-1]['text']
    from pypdf import PdfWriter
    from pypdf.generic import NameObject,DictionaryObject,DecodedStreamObject
    pdf=PdfWriter();page=pdf.add_blank_page(width=300,height=300)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):pdf._add_object(font)})})
    content=DecodedStreamObject();content.set_data(b'BT /F1 12 Tf 20 200 Td (Le budget est un outil de suivi.) Tj ET');page[NameObject('/Contents')]=pdf._add_object(content)
    pdf.add_blank_page(width=300,height=300);buffer=io.BytesIO();pdf.write(buffer)
    s=req(f'/api/support?id={sid}&kind=pdf&name=Support.pdf',raw=buffer.getvalue())
    assert 'outil de suivi' in s['supports'][-1]['text'] and s['supports'][-1]['warnings']
    req(f'/api/chunk?id={sid}&seq=0&seconds=5',raw=b'first-audio-part')
    req(f'/api/chunk?id={sid}&seq=0&seconds=5',raw=b'first-audio-part')
    assert req('/api/session/'+sid)['chunk_count']==1
    fails(f'/api/chunk?id={sid}&seq=0',raw=b'wrong-content')
    fails(f'/api/chunk?id={sid}&seq=2',raw=b'out-of-order')
    store.update(sid,status='interrupted')
    req(f'/api/chunk?id={sid}&seq=1&seconds=9',raw=b'second-part')
    req('/api/finalize',{'id':sid,'process':False})
    assert req('/api/session/'+sid+'/audio')==b'first-audio-partsecond-part'
    assert req('/api/session/'+sid+'/audio',headers={'Range':'bytes=0-4'})==b'first'
    req(f'/api/chunk?id={sid}&seq=1&seconds=9',raw=b'second-part')
    fails('/api/sessions',headers={'X-Local-Token':'bad'},code=403)
    quiz=[{'question':'Test','options':['A','B','C','D'],'correct':1,'quote':'Citation sûre'}]
    store.update(sid,quiz=quiz)
    s=req('/api/quiz',{'id':sid,'answers':[1]});assert s['attempts'][-1]['score']==1
    s=req('/api/quiz',{'id':sid,'answers':[0],'indices':[0]});assert s['attempts'][-1]['score']==0
    s=req('/api/card',{'id':sid,'key':'Test notion','known':False});assert s['cards']['Test notion']['due']>0
    s=req('/api/marker',{'id':sid,'seconds':6,'text':'Important'});assert s['markers'][0]['start']==6
    s=req('/api/support?id='+sid+'&kind=txt&name=Support',raw='Définition du budget'.encode());assert any('budget' in d['text'] for d in s['supports'])
    backup=req('/api/backup');z=zipfile.ZipFile(io.BytesIO(backup));assert z.read(sid+'/audio')==b'first-audio-partsecond-part';assert any(n.endswith('session.json') for n in z.namelist())
    # A generation update must retain user quiz and markers.
    store.update(sid,notes={'report':'Compte rendu'});s=store.read(sid);assert s['markers'] and s['attempts'] and s['cards']
    # A changed support must not pretend it was included in an already authored course.
    store.update(sid,notes={'course':'Un cours rédigé','report':'Compte rendu'},course_complete=True)
    s=req('/api/support?id='+sid+'&kind=txt&name=Nouveau',raw=b'Nouvelle source apres redaction')
    assert s['course_needs_refresh']
    try:
        req('/api/quiz/generate',{'id':sid,'count':6,'level':'approfondir'})
        raise AssertionError('Un quiz ne doit pas utiliser un cours périmé')
    except urllib.error.HTTPError as e:assert e.code==400
    options=req('/api/learning-settings',{'id':sid,'enrichment_enabled':True,'research_enabled':False})
    assert options['enrichment_enabled'] and not options['research_enabled'] and options['course_needs_refresh']
    store.update(sid,course_needs_refresh=False)
    imported=req('/api/import?process=false',raw=b'fake-audio-for-import-metadata',headers={'Content-Type':'audio/webm'})
    assert not imported['title_user_set'] and imported['status']=='saved'
    from unittest.mock import patch
    with patch.object(server,'enqueue',side_effect=lambda sid,action,**kwargs:store.update(sid,quiz_settings=kwargs['quiz_settings'])):
        s=req('/api/quiz/generate',{'id':sid,'count':6,'level':'approfondir','topic':'Budget','focus_errors':True})
    assert s['quiz_settings']['count']==6 and s['quiz_settings']['level']=='approfondir'
    http.shutdown()
print('Vérifié : sauvegarde progressive, doublons, récupération, lecture partielle, protection locale, quiz, cartes, marqueurs, supports et archive.')
