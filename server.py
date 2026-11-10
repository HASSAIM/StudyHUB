import json, os, threading, secrets, subprocess, sys, hashlib, shutil, zipfile, tempfile, re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from store import ROOT, DATA, folder, read, update, create, listing, assemble, atomic
TOKEN=secrets.token_urlsafe(32)
COMPUTE=threading.Lock()
BUSY={'queued','transcription','analyse','question'}
OFFLINE={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
def job(sid,action,extra=None):
    with COMPUTE:
        try:
            result=subprocess.run([sys.executable,str(ROOT/'worker.py'),sid,action]+([extra] if extra else []),cwd=ROOT,env=OFFLINE,capture_output=True,text=True)
            if result.returncode:raise RuntimeError(result.stderr[-500:])
        except Exception as e:update(sid,status='error',error='Traitement interrompu. Les données sauvegardées restent disponibles. '+str(e)[:500])
def enqueue(sid,action,extra=None,quiz_settings=None):
    from filelock import FileLock
    with FileLock(str(folder(sid)/'attachment.lock')):
        s=read(sid)
        if s['status'] in BUSY:raise ValueError('Ce cours est déjà en cours de traitement')
        if action=='quiz' and (not s.get('course_complete') or s.get('course_needs_refresh')):raise ValueError('Recrée le cours avant de personnaliser le quiz')
        if action=='transcribe' and not s.get('audio_available'):raise ValueError('Aucun audio sauvegardé pour ce cours')
        if s['status']=='recording':raise ValueError('Termine ou récupère d’abord l’enregistrement')
        update(sid,status='queued',progress=0,error=None,pending_action=action,pending_input=extra,**({'quiz_settings':quiz_settings} if quiz_settings is not None else {}))
    threading.Thread(target=job,args=(sid,action,extra),daemon=True).start();return read(sid)

class Handler(BaseHTTPRequestHandler):
    def host_ok(self):return self.headers.get('Host') in ('127.0.0.1:8765','localhost:8765')
    def authorized(self):
        q=parse_qs(urlparse(self.path).query)
        supplied=self.headers.get('X-Local-Token') or q.get('access',[''])[0]
        return self.host_ok() and secrets.compare_digest(supplied,TOKEN)
    def reply(self,obj,status=200):
        data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(data)
    def body(self,limit=200000):
        n=int(self.headers.get('Content-Length',0))
        if not 0<n<=limit:raise ValueError('Taille de requête invalide')
        return json.loads(self.rfile.read(n))
    def receive(self,target,limit):
        n=int(self.headers.get('Content-Length',0))
        if not 0<n<=limit:raise ValueError('Fichier vide ou trop volumineux')
        with target.open('wb') as out:
            remaining=n
            while remaining:
                b=self.rfile.read(min(1024*1024,remaining))
                if not b:raise ValueError('Envoi interrompu')
                out.write(b);remaining-=len(b)
            out.flush();os.fsync(out.fileno())
    def stream(self,p,mime,filename=None):
        size=p.stat().st_size;start=0;end=size-1;r=self.headers.get('Range')
        if r:
            m=re.fullmatch(r'bytes=(\d*)-(\d*)',r)
            if not m:return self.reply({'error':'Plage invalide'},416)
            if m[1]:start=int(m[1]);end=min(int(m[2]) if m[2] else end,end)
            elif m[2]:start=max(0,size-int(m[2]))
            if start>end:return self.reply({'error':'Plage invalide'},416)
        self.send_response(206 if r else 200);self.send_header('Content-Type',mime);self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.send_header('Referrer-Policy','no-referrer')
        if r:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        if filename:self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.end_headers()
        with p.open('rb') as inp:
            inp.seek(start);remaining=end-start+1
            while remaining:
                b=inp.read(min(1024*1024,remaining));self.wfile.write(b);remaining-=len(b)
    def do_GET(self):
        path=urlparse(self.path).path
        if not self.host_ok():return self.reply({'error':'Accès refusé'},403)
        if path=='/health':return self.reply({'app':'isc-cours-local','ready':True,'version':6})
        if path=='/':
            data=(ROOT/'index.html').read_text().replace('__TOKEN__',TOKEN).encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
        if path in ('/assets/studyhub-logo.png','/assets/favicon.png'):
            return self.stream(ROOT/path.lstrip('/'),'image/png')
        if not self.authorized():return self.reply({'error':'Recharge la page pour te reconnecter'},403)
        try:
            if path.startswith('/api/native/status/'):
                import native_audio
                sid=path.rsplit('/',1)[1];native_audio.heartbeat(sid)
                return self.reply(native_audio.status(sid))
            if path=='/api/sessions':return self.reply(listing())
            if path=='/api/storage':return self.reply({'path':str(DATA),'bytes':sum(p.stat().st_size for p in DATA.rglob('*') if p.is_file()),'free':shutil.disk_usage(DATA).free})
            if path=='/api/backup':
                fd,name=tempfile.mkstemp(suffix='.zip');os.close(fd);p=__import__('pathlib').Path(name)
                try:
                    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
                        for f in DATA.rglob('*'):
                            if f.is_file() and not f.name.endswith(('.tmp','.lock')):z.write(f,str(f.relative_to(DATA)))
                    self.stream(p,'application/zip','sauvegarde-cours.zip')
                finally:p.unlink(missing_ok=True)
                return
            if path.startswith('/api/session/'):
                parts=path.split('/');sid=parts[3];s=read(sid)
                if len(parts)==4:return self.reply(s)
                if parts[4]=='audio':
                    p=folder(sid)/'audio'
                    if not p.exists():p=assemble(sid)
                    return self.stream(p,s.get('mime','application/octet-stream'),'cours.'+('wav' if s.get('mime')=='audio/wav' else 'm4a' if 'mp4' in s.get('mime','') else 'webm'))
            return self.reply({'error':'Introuvable'},404)
        except (ValueError,OSError) as e:return self.reply({'error':str(e)},400)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_POST(self):
        if not self.authorized() or self.headers.get('Origin') not in ('http://127.0.0.1:8765','http://localhost:8765'):return self.reply({'error':'Accès refusé'},403)
        parsed=urlparse(self.path);q=parse_qs(parsed.query);path=parsed.path
        try:
            if path=='/api/native/start':
                import native_audio
                b=self.body();s=create(b.get('title'),b.get('language','fr'),b.get('subject',''),'audio/wav')
                try:
                    update(s['id'],vocabulary=str(b.get('vocabulary',''))[:500],enrichment_enabled=bool(b.get('enrichment_enabled',True)),research_enabled=bool(b.get('research_enabled',True)))
                    native_audio.start(s['id']);return self.reply(read(s['id']))
                except Exception as e:
                    update(s['id'],status='error',error=str(e));raise
            if path=='/api/start':
                b=self.body();s=create(b.get('title'),b.get('language','auto'),b.get('subject',''),b.get('mime','audio/webm'));return self.reply(update(s['id'],source=b.get('source','unknown'),vocabulary=str(b.get('vocabulary',''))[:500],enrichment_enabled=bool(b.get('enrichment_enabled',True)),research_enabled=bool(b.get('research_enabled',True))))
            if path=='/api/import':
                s=create(q.get('title',[''])[0],q.get('language',['auto'])[0],q.get('subject',[''])[0],self.headers.get('Content-Type','application/octet-stream'),status='saved')
                update(s['id'],enrichment_enabled=q.get('enrich',['true'])[0]!='false',research_enabled=q.get('research',['true'])[0]!='false');p=folder(s['id']);self.receive(p/'audio.tmp',1024**3);os.replace(p/'audio.tmp',p/'audio');return self.reply(enqueue(s['id'],'transcribe') if q.get('process',['true'])[0]!='false' else read(s['id']))
            if path=='/api/chunk':
                sid=q['id'][0];seq=int(q['seq'][0]);seconds=float(q.get('seconds',['0'])[0]);p=folder(sid)
                if not 0<=seq<100000:raise ValueError('Numéro de morceau invalide')
                from filelock import FileLock
                with FileLock(str(p/'chunk.lock')):
                    s=read(sid)
                    if s['status'] not in ('recording','interrupted') and not (p/'chunks'/f'{seq:08d}.chunk').exists():raise ValueError('L’enregistrement est déjà terminé')
                    dest=p/'chunks'/f'{seq:08d}.chunk';temp=p/'chunks'/f'{seq:08d}.tmp';self.receive(temp,64*1024**2)
                    if dest.exists():
                        if hashlib.sha256(dest.read_bytes()).digest()!=hashlib.sha256(temp.read_bytes()).digest():temp.unlink();raise ValueError('Le morceau existe avec un contenu différent')
                        temp.unlink()
                    else:
                        if seq!=s.get('chunk_count',0):temp.unlink();raise ValueError('Un morceau précédent manque')
                        os.replace(temp,dest);update(sid,chunk_count=seq+1,saved_seconds=seconds)
                return self.reply(read(sid))
            if path=='/api/support':
                from filelock import FileLock
                sid=q['id'][0]
                with FileLock(str(folder(sid)/'attachment.lock')):
                    s=read(sid)
                    if s['status'] in BUSY:raise ValueError('Attends la fin du traitement avant d’importer un support')
                    kind=q.get('kind',[''])[0];name=q.get('name',['Support'])[0][:150]
                    if kind not in ('pdf','pptx','docx','txt'):raise ValueError('Choisis un PDF, un PowerPoint .pptx, un Word .docx ou un texte .txt')
                    upload_key=q.get('key',[''])[0][:100]
                    p=folder(sid)/('support-'+secrets.token_hex(8)+'.'+kind)
                    try:
                        self.receive(p,50*1024**2);digest=hashlib.sha256(p.read_bytes()).hexdigest()
                        duplicate=next((d for d in s.get('supports',[]) if upload_key and d.get('upload_key')==upload_key),None)
                        if duplicate:
                            if duplicate.get('sha256')!=digest:raise ValueError('Ce support existe déjà avec un contenu différent')
                            p.unlink();return self.reply(read(sid))
                        warnings=[]
                        if kind=='pdf':
                            from pypdf import PdfReader
                            reader=PdfReader(p)
                            pages=[page.extract_text() or '' for page in reader.pages]
                            text='\n'.join(f'Page {i+1}\n'+content for i,content in enumerate(pages))
                            missing=sum(not content.strip() for content in pages)
                            if missing:warnings.append(str(missing)+' page(s) sans texte : images ou scans non analysés.')
                            if not any(content.strip() for content in pages):raise ValueError('Ce PDF est un scan sans texte extractible. Ajoute une version avec du texte.')
                        elif kind=='pptx':
                            from pptx import Presentation
                            slides=[]
                            for i,slide in enumerate(Presentation(p).slides):
                                parts=[]
                                for shape in slide.shapes:
                                    if shape.has_text_frame:parts.append(shape.text)
                                    if shape.has_table:parts.extend(' | '.join(cell.text for cell in row.cells) for row in shape.table.rows)
                                content='\n'.join(parts)
                                if not content.strip():warnings.append('Diapositive '+str(i+1)+' sans texte extractible.')
                                slides.append('Diapositive '+str(i+1)+'\n'+content)
                            text='\n'.join(slides)
                            if not any(line.strip() for line in text.splitlines() if not line.startswith('Diapositive ')):raise ValueError('Aucun texte extractible dans ce PowerPoint. Les images ne sont pas reconnues.')
                        elif kind=='docx':
                            import xml.etree.ElementTree as ET
                            with zipfile.ZipFile(p) as archive:
                                if archive.getinfo('word/document.xml').file_size>10*1024**2:raise ValueError('Le texte de ce Word est trop volumineux. Découpe-le en plusieurs fichiers.')
                                document=ET.fromstring(archive.read('word/document.xml'))
                            namespace={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                            text='\n'.join(''.join(node.text or '' for node in paragraph.findall('.//w:t',namespace)) for paragraph in document.findall('.//w:p',namespace))
                        else:
                            try:text=p.read_text(encoding='utf-8-sig')
                            except UnicodeDecodeError:text=p.read_text(encoding='cp1252')
                        if not text.strip():raise ValueError('Aucun texte extractible. Les images et les scans ne sont pas reconnus.')
                        if len(text)>500000:raise ValueError('Ce support est trop long. Découpe-le en plusieurs documents pour conserver tout son contenu.')
                        supports=s.get('supports',[])+[{'name':name,'file':p.name,'text':text,'upload_key':upload_key,'sha256':digest,'warnings':warnings}]
                        return self.reply(update(sid,supports=supports,course_needs_refresh=bool(s.get('notes',{}).get('course'))))
                    except Exception:
                        p.unlink(missing_ok=True);raise
            b=self.body();sid=b['id'];s=read(sid)
            if path=='/api/support/delete':
                from filelock import FileLock
                with FileLock(str(folder(sid)/'attachment.lock')):
                    s=read(sid)
                    if s['status'] in BUSY:raise ValueError('Attends la fin du traitement avant de retirer un support')
                    document=next((d for d in s.get('supports',[]) if d['file']==b.get('file')),None)
                    if not document:raise ValueError('Support introuvable')
                    # Only a server-generated basename from the session metadata is accepted.
                    if __import__('pathlib').Path(document['file']).name!=document['file']:raise ValueError('Support invalide')
                    supports=[d for d in s.get('supports',[]) if d['file']!=document['file']]
                    result=update(sid,supports=supports,course_needs_refresh=bool(s.get('notes',{}).get('course')))
                    (folder(sid)/document['file']).unlink(missing_ok=True)
                    return self.reply(result)
            if path=='/api/native/control':
                import native_audio
                return self.reply(native_audio.stop(sid) if b.get('action')=='stop' else native_audio.control(sid,b.get('action')))
            if path=='/api/finalize':
                if s.get('native_audio'):
                    import native_audio
                    native_audio.stop(sid)
                    if not (folder(sid)/'audio').exists() or (folder(sid)/'audio').stat().st_size<=44:raise ValueError('Aucun son sauvegardé. Vérifie les autorisations audio du Mac et réessaie.')
                from filelock import FileLock
                with FileLock(str(folder(sid)/'chunk.lock')):
                    assemble(sid);update(sid,status='saved')
                return self.reply(enqueue(sid,'transcribe') if b.get('process',True) else read(sid))
            if path=='/api/transcribe':return self.reply(enqueue(sid,'transcribe'))
            if path=='/api/learning-settings':
                if s['status'] in BUSY:raise ValueError('Attends la fin de la création du cours pour changer ces options')
                return self.reply(update(sid,enrichment_enabled=bool(b.get('enrichment_enabled',True)),research_enabled=bool(b.get('research_enabled',True)),course_needs_refresh=bool(s.get('notes',{}).get('course'))))
            if path=='/api/quiz/generate':
                if s['status'] in BUSY or not s.get('notes',{}).get('course') or not s.get('course_complete') or s.get('course_needs_refresh'):raise ValueError('Attends que le cours rédigé soit prêt avant de créer un quiz personnalisé')
                count=b.get('count',4);level=b.get('level','comprendre')
                if type(count) is not int or count not in (4,6,8) or level not in ('comprendre','appliquer','approfondir'):raise ValueError('Choisis un niveau et 4, 6 ou 8 questions')
                return self.reply(enqueue(sid,'quiz',quiz_settings={'count':count,'level':level,'topic':str(b.get('topic',''))[:150],'focus_errors':bool(b.get('focus_errors',True))}))
            if path=='/api/analyze':
                if not s.get('transcript'):raise ValueError('La transcription n’est pas encore disponible')
                return self.reply(enqueue(sid,'analyze'))
            if path=='/api/ask':
                question=str(b.get('question','')).strip()[:1000]
                if not question or not s.get('transcript'):raise ValueError('Pose une question après la transcription')
                return self.reply(enqueue(sid,'ask',question))
            if path=='/api/marker':
                markers=s.get('markers',[])+[{'start':max(0,float(b['seconds'])),'text':str(b.get('text','Important'))[:500]}];return self.reply(update(sid,markers=markers))
            if path=='/api/edit':
                if s['status'] in BUSY:raise ValueError('Attends la fin du traitement avant de modifier le cours')
                return self.reply(update(sid,title=str(b.get('title',s['title'])).strip()[:150] or s['title'],title_user_set=True,title_origin='user',subject=str(b.get('subject',s.get('subject','')))[:100]))
            if path=='/api/quiz':
                all_questions=s.get('quiz',[]);indices=b.get('indices',list(range(len(all_questions))))
                if not indices or len(set(indices))!=len(indices) or any(type(i) is not int or i not in range(len(all_questions)) for i in indices):raise ValueError('Sélection de questions invalide')
                questions=[all_questions[i] for i in indices];answers=b.get('answers',[])
                if len(answers)!=len(questions) or any(not isinstance(a,int) or a not in range(4) for a in answers):raise ValueError('Réponds à chaque question')
                score=sum(a==item['correct'] for a,item in zip(answers,questions));attempt={'created':__import__('time').time(),'score':score,'total':len(questions),'answers':answers,'quiz':questions}
                return self.reply(update(sid,attempts=s.get('attempts',[])+[attempt]))
            if path=='/api/card':
                key=str(b['key']);cards=s.get('cards',{});known=bool(b.get('known'));cards[key]={'known':known,'due':__import__('time').time()+(3*86400 if known else 86400)};return self.reply(update(sid,cards=cards))
            return self.reply({'error':'Action inconnue'},404)
        except (ValueError,KeyError,OSError,json.JSONDecodeError) as e:return self.reply({'error':str(e)},400)
        except Exception as e:return self.reply({'error':'Action impossible : '+str(e)[:250]},500)
    def log_message(self,*args):pass
if __name__=='__main__':
    resume=[]
    for s in listing():
        if s['status'] in ('recording','interrupted'):
            if s.get('native_audio'):
                import native_audio
                native_audio.control(s['id'],'stop')
            update(s['id'],status='interrupted')
        elif s['status'] in BUSY:
            action=s.get('pending_action') or ('analyze' if s.get('transcript') else 'transcribe');update(s['id'],status='saved');resume.append((s['id'],action,s.get('pending_input')))
    print('StudyHUB v6 : http://127.0.0.1:8765',flush=True)
    server=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    for sid,action,extra in resume:enqueue(sid,action,extra)
    server.serve_forever()
