import json, os, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
URL='http://127.0.0.1:8765/'
def ready():
    try:
        with urllib.request.urlopen(URL+'health',timeout=1) as response:
            data=json.load(response)
            return data.get('app')=='isc-cours-local' and data.get('version',0)>=5
    except Exception:return False

def ensure_running():
    if ready():return
    with (ROOT/'runtime.log').open('ab') as log:
        subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,stdout=log,stderr=log,start_new_session=True,env={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'})
    for _ in range(40):
        if ready():return
        time.sleep(0.25)
    raise RuntimeError('Le programme local ne démarre pas. Consulte runtime.log dans le dossier Cours ISC.')
if __name__=='__main__':ensure_running();print('StudyHUB est lancé indépendamment de cette conversation.')
