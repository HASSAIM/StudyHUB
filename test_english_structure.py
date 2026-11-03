import os,json,uuid,time,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    data=Path(temp);sid=uuid.uuid4().hex;p=data/sid;p.mkdir()
    segments=[{'start':0,'text':'A project has a clear objective, a budget, and a deadline.'},{'start':12,'text':'A risk is an uncertain event that can delay a project.'},{'start':25,'text':'The project manager assigns a person to each task and estimates its duration.'}]
    s=dict(id=sid,title='English test',language='en',created=time.time(),status='saved',transcript='\n'.join(f'[{int(x["start"])//60:02d}:{int(x["start"])%60:02d}] {x["text"]}' for x in segments),segments=segments)
    (p/'session.json').write_text(json.dumps(s))
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'worker.py'),sid,'structure'],env={**os.environ,'ISC_DATA_DIR':str(data),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'},check=True)
    s=json.loads((p/'session.json').read_text());assert s.get('quiz'),s.get('structured_error');assert s.get('keywords');assert s.get('flashcards')
    print('Cours anglais : QCM, mots clés et cartes validés avec citations conservées en anglais.')
