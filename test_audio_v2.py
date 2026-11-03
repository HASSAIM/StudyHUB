import os, tempfile, subprocess, json, uuid, time
from pathlib import Path
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temp:
    data=Path(temp);src=Path('/private/tmp/isc-audio-test.aiff')
    if not src.exists():raise RuntimeError('Audio de test absent')
    webm=data/'test.webm'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-i',str(src),'-c:a','libopus',str(webm)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sid=uuid.uuid4().hex;p=data/sid;p.mkdir();(p/'chunks').mkdir();audio=webm.read_bytes();half=len(audio)//2
    (p/'chunks'/'00000000.chunk').write_bytes(audio[:half]);(p/'chunks'/'00000001.chunk').write_bytes(audio[half:])
    (p/'session.json').write_text(json.dumps(dict(id=sid,title='Audio de test',created=time.time(),language='en',status='interrupted',transcript='')))
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'worker.py'),sid,'transcribe-only'],env={**os.environ,'ISC_DATA_DIR':str(data),'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'},check=True)
    s=json.loads((p/'session.json').read_text());assert 'project' in s['transcript'].lower();assert s['segments'];assert s['duration']>1
print('Audio WebM reconstitué à partir de morceaux, puis transcrit hors ligne avec horodatages.')
