"""Local macOS system-audio capture. No microphone, browser upload or screen image."""
import json,os,plistlib,shutil,subprocess,sys,threading,time
from pathlib import Path
from store import ROOT,folder,read,update,atomic
LOCK=threading.RLock()
APP=ROOT/'native-build'/'StudyHUB Audio.app'

def build():
    if sys.platform!='darwin':raise ValueError('La capture directe du son du Mac nécessite macOS.')
    source=ROOT/'native/SystemAudio.swift';binary=APP/'Contents/MacOS/StudyHUBAudio'
    if binary.exists() and binary.stat().st_mtime>=source.stat().st_mtime:return binary
    if not shutil.which('xcrun'):raise ValueError('Les outils de développement Apple sont nécessaires pour préparer la capture audio locale.')
    binary.parent.mkdir(parents=True,exist_ok=True)
    sdks=Path('/Library/Developer/CommandLineTools/SDKs');compatible=sdks/'MacOSX15.4.sdk'
    sdk=['-sdk',str(compatible)] if compatible.exists() else []
    result=subprocess.run(['xcrun','swiftc','-parse-as-library']+sdk+[str(source),'-o',str(binary),'-framework','ScreenCaptureKit','-framework','AVFoundation','-module-cache-path',str(ROOT/'native-build/cache')],capture_output=True,text=True,timeout=120)
    if result.returncode:raise ValueError('La capture audio native n’a pas pu être préparée. '+result.stderr[-300:])
    (APP/'Contents/Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'local.studyhub.systemaudio','CFBundleName':'StudyHUB Audio','CFBundleDisplayName':'StudyHUB Audio','CFBundleExecutable':'StudyHUBAudio','CFBundlePackageType':'APPL','LSUIElement':True,'NSAudioCaptureUsageDescription':'Enregistrer le son du cours sur ce Mac pour créer ton cours dans StudyHUB.','NSScreenCaptureUsageDescription':'Capturer uniquement le son du Mac. Aucune image d’écran ni microphone n’est enregistré.'}))
    subprocess.run(['codesign','--force','--deep','--sign','-',str(APP)],capture_output=True,check=True)
    return binary

def status(sid):
    p=folder(sid)/'native-status.json'
    try:return json.loads(p.read_text())
    except (OSError,ValueError):return {'state':'starting','seconds':0,'level':0}

def heartbeat(sid):
    p=folder(sid)/'native-control.json'
    with LOCK:
        try:command=json.loads(p.read_text())
        except (OSError,ValueError):return
        command['lease']=time.time();atomic(p,command)

def control(sid,action):
    if action not in ('pause','resume','stop'):raise ValueError('Commande audio invalide')
    if not read(sid).get('native_audio'):raise ValueError('Ce cours n’utilise pas la capture native')
    with LOCK:atomic(folder(sid)/'native-control.json',{'action':action,'lease':time.time()})
    return status(sid)

def start(sid):
    with LOCK:
        # Only one system-audio capture per Mac.
        from store import listing
        for s in listing():
            if s['id']!=sid and s.get('native_audio') and s.get('status')=='recording' and status(s['id']).get('state') in ('recording','paused','permission','starting'):
                raise ValueError('Un autre enregistrement du son du Mac est déjà ouvert.')
        build();atomic(folder(sid)/'native-control.json',{'action':'resume','lease':time.time()})
        atomic(folder(sid)/'native-status.json',{'state':'starting','seconds':0,'level':0})
        update(sid,native_audio=True,mime='audio/wav',source='system')
        log=(folder(sid)/'native.log').open('ab')
        process=subprocess.Popen(['/usr/bin/open','-n','-W',str(APP),'--args',str(folder(sid))],stdout=log,stderr=log)
        def monitor():
            process.wait();log.close()
            s=status(sid)
            if s.get('state') not in ('stopped','error'):atomic(folder(sid)/'native-status.json',{'state':'error','error':'La capture du son du Mac a été interrompue. Les données déjà écrites sont conservées.','seconds':s.get('seconds',0),'level':0})
            current=read(sid)
            if current.get('status')=='recording':
                update(sid,status='interrupted' if s.get('bytes',0)>0 else 'error',saved_seconds=s.get('seconds',0),error=s.get('error') or None)
        threading.Thread(target=monitor,daemon=True).start()
        return status(sid)

def stop(sid):
    control(sid,'stop')
    for _ in range(60):
        state=status(sid)
        if state.get('state') in ('stopped','error'):
            update(sid,saved_seconds=state.get('seconds',0));return state
        time.sleep(.1)
    raise ValueError('La capture est en train de s’arrêter. Réessaie dans quelques secondes.')
