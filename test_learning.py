import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import store,worker

class LearningTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.original=store.DATA;store.DATA=Path(self.tmp.name)
  self.session=store.create('', 'fr');worker.SID=self.session['id'];worker.ACTION='analyze'
  store.update(worker.SID,enrichment_enabled=False,research_enabled=False,transcript='[00:00] Le budget regroupe les recettes et les dépenses prévues.',segments=[{'start':0,'text':'Le budget regroupe les recettes et les dépenses prévues.'}],supports=[{'name':'Support du professeur','file':'support-a.txt','text':'Page 1\nUne marge de sécurité couvre les risques identifiés.'}])
  self.calls=[]
 def tearDown(self):store.DATA=self.original;self.tmp.cleanup()
 def fake_answer(self,instruction,source,limit=1500):
  self.calls.append((instruction,source))
  if 'Prépare un VRAI COURS' in instruction:return json.dumps({'title':'Construire et sécuriser le budget d’un projet','objective':'Comprendre le budget et ses risques.','chapters':[{'title':'Le budget prévisionnel','scope':'recettes et dépenses'},{'title':'Sécuriser le projet','scope':'marge et risques du support S1'}]})
  if 'Vérifie strictement' in instruction:return json.dumps({'supported':['B'+str(i+1) for i in range(len(json.loads(source)))]})
  if 'Rédige le chapitre' in instruction:return json.dumps({'blocks':[{'heading':'Comprendre le budget','explanation':'Le budget rassemble les recettes et les dépenses prévues. Le support ajoute que la marge de sécurité couvre les risques identifiés.','evidence':['O1','S1-1']}]})
  if 'Prépare Les' in instruction or 'Prépare Des questions' in instruction:return json.dumps({'items':[{'heading':'La marge de sécurité','explanation':'Elle couvre les risques identifiés.','evidence':['S1-1']}]})
  if 'UNIQUEMENT un objet JSON' in instruction:return json.dumps({'quiz':[{'question':'À quoi sert la marge de sécurité ?','options':['Couvrir les risques identifiés','Remplacer les recettes','Supprimer les dépenses','Supprimer le budget'],'correct':0,'explanation':'Le support précise le rôle de la marge.','evidence':['S1-1']}],'keywords':[{'term':'Budget','definition':'Recettes et dépenses prévues','evidence':['O1']}],'flashcards':[{'front':'Rôle de la marge ?','back':'Couvrir les risques identifiés','evidence':['S1-1']}]})
  return '### Explication\nLe budget rapproche les recettes et les dépenses prévues [00:00]. La marge de sécurité couvre les risques identifiés dans le support [S1, p. 1].\n### À retenir\n- Prévoir les dépenses et les risques.'
 def test_malformed_json_retried_once_before_validation(self):
  with patch.object(worker,'answer',side_effect=['{"quiz":', '{"quiz":[]}']) as model:
   self.assertEqual(worker.answer_json('Créer un quiz','Preuves',500),{'quiz':[]});self.assertEqual(model.call_count,2)
  with patch.object(worker,'answer',return_value='JSON invalide') as model:
   with self.assertRaises(ValueError):worker.answer_json('Créer un quiz','Preuves',500)
   self.assertEqual(model.call_count,2)
 def test_full_course_and_original_evidence(self):
  with patch.object(worker,'answer',side_effect=self.fake_answer):worker.analyze()
  s=store.read(worker.SID);self.assertTrue(s['course_complete']);self.assertEqual(s['title_origin'],'ia');self.assertIn('## 2.',s['notes']['course']);self.assertIn('S1',s['notes']['course']);self.assertEqual(s['quiz'][0]['source_type'],'support');self.assertIsNone(s['quiz'][0]['start']);self.assertEqual(s['flashcards'][0]['source_name'],'Support du professeur');self.assertEqual(s['status'],'termine')
  quiz_source=next(source for instruction,source in self.calls if 'UNIQUEMENT un objet JSON' in instruction);self.assertIn('COURS RÉDIGÉ',quiz_source);self.assertIn('SUPPORT ÉCRIT',quiz_source)
 def test_complete_pipeline_can_enrich_after_source_grounding(self):
  store.update(worker.SID,enrichment_enabled=True,research_enabled=False)
  body='Le budget de projet sert à préparer les décisions avant les dépenses. '+('Les hypothèses de ressources doivent être explicites pour pouvoir ensuite comprendre les écarts et adapter les décisions. '*5)
  payload=json.dumps({'sections':[{'heading':'Comprendre le rôle du budget','body':body,'kind':'explanation'}]})
  with patch.object(worker,'answer',side_effect=self.fake_answer),patch.object(worker,'teach_answer',return_value=payload):worker.analyze()
  s=store.read(worker.SID);self.assertTrue(s['course_complete']);self.assertTrue(s['course_is_enriched']);self.assertIn('foundation',s['notes']);self.assertNotIn('[00:00]',s['notes']['course']);self.assertTrue(s['quiz']);self.assertEqual(s['research']['status'],'disabled')
 def test_manual_title_preserved(self):
  store.update(worker.SID,title='Mon titre personnel',title_user_set=True)
  with patch.object(worker,'answer',side_effect=self.fake_answer):worker.analyze()
  s=store.read(worker.SID);self.assertEqual(s['title'],'Mon titre personnel');self.assertTrue(s['notes']['course'].startswith('# Mon titre personnel'))
 def test_generated_text_not_accepted_as_evidence(self):
  s=store.read(worker.SID);s['notes']={'course':'Une affirmation inventée ne figure pas dans les sources.'}
  self.assertIsNone(worker.locate_quote({'quote':'Une affirmation inventée ne figure pas dans les sources.'},s))
  self.assertIsNone(worker.locate_quote({'quote':'Une marge de sécurité couvre les risques identifiés.','source':'oral'},s))
 def test_partial_course_saved_on_interruption(self):
  def interrupted(instruction,source,limit=1500):
   if 'Rédige le chapitre 2' in instruction:raise RuntimeError('Interruption simulée')
   return self.fake_answer(instruction,source,limit)
  with patch.object(worker,'answer',side_effect=interrupted):
   with self.assertRaises(RuntimeError):worker.analyze()
  s=store.read(worker.SID);self.assertFalse(s['course_complete']);self.assertEqual(s['course_chapters_done'],1);self.assertIn('budget',s['notes']['course'])
 def test_long_sources_are_all_read(self):
  s=store.read(worker.SID);s['supports'][0]['text']='Introduction\n'+'Notion utile. '*3000+'\nDERNIERE_PAGE_IMPORTANTE'
  seen=[]
  def digest(instruction,source,limit):seen.append(source);return source[-400:]
  with patch.object(worker,'answer',side_effect=digest):result=worker.learning_sources(s)
  self.assertTrue(any('DERNIERE_PAGE_IMPORTANTE' in item for item in seen));self.assertIn('DERNIERE_PAGE_IMPORTANTE',result)
 def test_personalization_uses_previous_errors(self):
  s=store.read(worker.SID);s['quiz_settings']={'count':6,'level':'approfondir','topic':'Budget','focus_errors':True};s['attempts']=[{'quiz':[{'question':'Quelle marge prévoir ?','correct':0}],'answers':[1]}]
  with patch.object(worker,'answer',side_effect=self.fake_answer):worker.structure(s)
  instruction=next(i for i,_ in self.calls if 'UNIQUEMENT un objet JSON' in i);self.assertIn('Quelle marge prévoir ?',instruction);self.assertIn('approfondir',instruction)

 def test_novel_numbers_and_unknown_evidence_rejected(self):
  bank=worker.evidence_bank(store.read(worker.SID))
  items=[{'heading':'Exemple inventé','explanation':'Le budget est de 100000 euros.','evidence':['O1']},{'heading':'Fausse preuve','explanation':'Le budget regroupe les dépenses.','evidence':['O99']},{'heading':'Budget','explanation':'Le budget prévoit recettes et dépenses.','evidence':['O1']}]
  accepted=worker.grounded_items(items,bank,('heading','explanation'));self.assertEqual(len(accepted),1);self.assertEqual(accepted[0]['heading'],'Budget')
 def test_placeholder_headings_are_replaced(self):
  self.assertEqual(worker.learning_heading('notion ou question','Un budget prévisionnel regroupe les recettes et les dépenses.'),'Un budget prévisionnel')
  self.assertTrue(worker.learning_heading('notion ou question','Un budget prévisionnel regroupe les recettes.','questions').startswith('À expliquer :'))
 def test_inline_evidence_does_not_create_numeric_false_alarm(self):
  bank=worker.evidence_bank(store.read(worker.SID));item={'heading':'Budget','explanation':'Le budget regroupe recettes et dépenses [O1].','evidence':['O1']}
  result=worker.grounded_items([item],bank,('heading','explanation'));self.assertEqual(len(result),1);self.assertNotIn('[O1]',result[0]['explanation'])
  del item['evidence'];self.assertEqual(len(worker.grounded_items([item],bank,('heading','explanation'))),1)
 def test_reviewer_can_reject_unsupported_method(self):
  bank=worker.evidence_bank(store.read(worker.SID));items=[{'heading':'Méthode','explanation':'Utiliser la méthode WBS pour calculer une marge.','evidence':['O1']}]
  with patch.object(worker,'answer',return_value='{"supported":[]}'):self.assertEqual(worker.review_grounding(items,bank,('heading','explanation')),[])

if __name__=='__main__':unittest.main()
