import json, os, re, uuid, time
from pathlib import Path
from filelock import FileLock
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('ISC_DATA_DIR',str(ROOT/'sessions')));DATA.mkdir(exist_ok=True)
def folder(sid):
    if not isinstance(sid,str) or not re.fullmatch(r'[a-f0-9]{32}',sid): raise ValueError('Cours inconnu')
    p=DATA/sid
    if not p.is_dir(): raise ValueError('Cours introuvable')
    return p
def read(sid):
    s=json.loads((folder(sid)/'session.json').read_text())
    if 'segments' not in s:
        s['segments']=[]
        for line in s.get('transcript','').splitlines():
            m=re.match(r'\[(\d+):(\d+)\]\s*(.*)',line)
            if m: s['segments'].append({'start':int(m[1])*60+int(m[2]),'text':m[3]})
    s['audio_available']=(folder(sid)/'audio').exists() or bool(list((folder(sid)/'chunks').glob('*.chunk')))
    if s.get('native_audio') and (folder(sid)/'audio').exists() and (folder(sid)/'audio').stat().st_size<=44:s['audio_available']=False
    return s
def update(sid,**fields):
    p=folder(sid)
    with FileLock(str(p/'session.lock')):
        s=read(sid);s.update(fields);atomic(p/'session.json',s)
    return s
def atomic(path,obj):
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with tmp.open('w') as out:
        json.dump(obj,out,ensure_ascii=False);out.flush();os.fsync(out.fileno())
    os.replace(tmp,path)
def create(title,language,subject='',mime='audio/webm',status='recording'):
    if language not in ('auto','fr','en'):raise ValueError('Langue invalide')
    title=str(title or '').strip();sid=uuid.uuid4().hex;p=DATA/sid;p.mkdir();(p/'chunks').mkdir()
    s=dict(id=sid,title_user_set=bool(title),title_origin='user' if title else 'pending',title=str(title or 'Cours sans titre')[:150],subject=str(subject)[:100],language=language,mime=mime,created=time.time(),status=status,progress=0,transcript='',segments=[],markers=[],notes={},quiz=[],attempts=[],cards={},supports=[],chat=[],saved_seconds=0,chunk_count=0)
    atomic(p/'session.json',s);return s
def listing():
    result=[]
    for p in DATA.glob('*/session.json'):
        try:result.append(read(p.parent.name))
        except (ValueError,OSError):continue
    return sorted(result,key=lambda s:s['created'],reverse=True)
def assemble(sid):
    p=folder(sid);files=sorted((p/'chunks').glob('*.chunk'))
    if not files:
        if (p/'audio').exists(): return p/'audio'
        raise ValueError('Aucun morceau audio sauvegardé')
    with (p/'audio.tmp').open('wb') as out:
        for f in files:
            with f.open('rb') as inp:
                while chunk:=inp.read(1024*1024):out.write(chunk)
        out.flush();os.fsync(out.fileno())
    os.replace(p/'audio.tmp',p/'audio');return p/'audio'
