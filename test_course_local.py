"""Integration test: real local model, fictional oral and written teaching sources."""
import json,os,subprocess,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as temporary:
 env={**os.environ,'ISC_DATA_DIR':temporary,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
 bootstrap='''import store,json\ns=store.create('', 'fr', 'Gestion de projet',status='saved')\nstore.update(s['id'],enrichment_enabled=False,research_enabled=False,transcript='[00:00] Un budget prévisionnel regroupe les recettes et les dépenses attendues du projet.\\n[00:15] Pour estimer le budget, on liste les tâches, on estime les ressources nécessaires et on chiffre chaque dépense.\\n[00:30] On compare ensuite le coût réel au coût prévu pour repérer les écarts et adapter le projet.\\n[00:45] Le professeur demande de présenter le budget de la conférence lors de la prochaine séance.',segments=[{'start':0,'text':'Un budget prévisionnel regroupe les recettes et les dépenses attendues du projet.'},{'start':15,'text':'Pour estimer le budget, on liste les tâches, on estime les ressources nécessaires et on chiffre chaque dépense.'},{'start':30,'text':'On compare ensuite le coût réel au coût prévu pour repérer les écarts et adapter le projet.'},{'start':45,'text':'Le professeur demande de présenter le budget de la conférence lors de la prochaine séance.'}],supports=[{'name':'Support budget du professeur.txt','file':'support.txt','text':'Page 1\\nUne marge de sécurité couvre les risques identifiés. Les risques sont évalués selon leur probabilité et leur impact.\\nPage 2\\nLe suivi du budget comprend le coût prévu, le coût réel et leur écart. Un écart positif du coût réel par rapport au coût prévu signale un dépassement.'}])\nprint(s['id'])'''
 sid=subprocess.check_output([str(ROOT/'.venv/bin/python'),'-c',bootstrap],cwd=ROOT,env=env,text=True).strip()
 process=subprocess.Popen([str(ROOT/'.venv/bin/python'),str(ROOT/'worker.py'),sid,'analyze'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 path=Path(temporary)/sid/'session.json';previous=None
 while process.poll() is None:
  s=json.loads(path.read_text());stage=s.get('analysis_stage')
  if stage!=previous:print(stage or 'Démarrage',flush=True);previous=stage
  time.sleep(2)
 stdout,stderr=process.communicate()
 if process.returncode:raise RuntimeError(stderr[-2500:])
 s=json.loads(path.read_text());assert s['course_complete'];assert len(s['notes']['course'])>600;assert s['title_origin']=='ia';assert '[S1' in s['notes']['course'];assert s['status']=='termine';assert s.get('quiz'),s.get('structured_error')
 report=ROOT/'verification-cours-ia.json';report.write_text(json.dumps({'scope':'Sources fictives courtes, modèle local réel, pas un cours long réel','title':s['title'],'course':s['notes']['course'],'points':s['notes']['report'],'quiz':s['quiz'],'flashcards':s['flashcards'],'chapters':s['course_chapters_done'],'sources':s['course_supports']},ensure_ascii=False,indent=2))
 print('Modèle local réel : cours rédigé, titre automatique, support écrit cité et quiz validé.',flush=True)
