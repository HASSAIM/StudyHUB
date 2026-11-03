"""Real local-model enrichment + real public research, using fictional course material."""
import os,sys,time,json,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temporary:
 env={**os.environ,'ISC_DATA_DIR':temporary,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
 bootstrap='''import store\ns=store.create('', 'fr', 'Gestion de projet',status='saved')\nstore.update(s['id'],title='Construire et suivre un budget de projet',title_user_set=False,title_origin='ia',transcript='[00:00] Le budget regroupe les recettes et les dépenses attendues.\\n[00:15] On compare le coût réel au coût prévu pour repérer les écarts.',segments=[{'start':0,'text':'Le budget regroupe les recettes et les dépenses attendues.'},{'start':15,'text':'On compare le coût réel au coût prévu pour repérer les écarts.'}],notes={'course':'# Construire et suivre un budget\\n\\nLe budget regroupe les recettes et les dépenses attendues. Pour le préparer, on liste les tâches et les ressources puis on chiffre les dépenses. Le suivi compare le coût réel au coût prévu pour adapter le projet.'},course_plan=[{'title':'Construire et suivre un budget','scope':'Préparation, suivi, interprétation des écarts et exemple pédagogique'}])\nprint(s['id'])'''
 sid=subprocess.check_output([str(ROOT/'.venv/bin/python'),'-c',bootstrap],cwd=ROOT,env=env,text=True).strip();start=time.monotonic()
 process=subprocess.Popen([str(ROOT/'.venv/bin/python'),str(ROOT/'worker.py'),sid,'enrich'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);path=Path(temporary)/sid/'session.json';previous=None
 while process.poll() is None:
  s=json.loads(path.read_text());stage=s.get('analysis_stage')
  if stage!=previous:print(stage or 'Démarrage',flush=True);previous=stage
  time.sleep(2)
 _,stderr=process.communicate()
 if process.returncode:raise RuntimeError(stderr[-2500:])
 s=json.loads(path.read_text())
 if s.get('structured_error'):
  import shutil
  diagnostic=Path(tempfile.mkdtemp(prefix='studyhub-test-'))/'session'
  shutil.copytree(path.parent,diagnostic);print('Diagnostic fictif conservé :',diagnostic,flush=True)
 assert s['course_complete'] and s['course_is_enriched'];assert len(s['notes']['course'])>1200;assert '[00:' not in s['notes']['course'];assert 'Exemple pédagogique' in s['notes']['course'];assert '= **' in s['notes']['course'];assert 'Clarifications et corrections' not in s['notes']['course'];assert 'budget personnel' not in s['notes']['course'].lower();assert s['research']['status']=='ok',s['research'];assert s.get('quiz'),s.get('structured_error')
 report={'scope':'Sources fictives courtes, modèle local et recherches publiques réels','seconds':round(time.monotonic()-start),'title':s['title'],'course':s['notes']['course'],'research':s['research'],'quiz':s['quiz']}
 (ROOT/'verification-enrichissement.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Cours approfondi, recherches réelles et quiz validés.',flush=True)
