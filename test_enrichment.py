import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import store,worker
class EnrichmentTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=store.DATA;store.DATA=Path(self.tmp.name);self.s=store.create('Budget','fr',status='saved');worker.SID=self.s['id']
  self.foundation='Le budget regroupe les recettes et les dépenses. [00:00]';self.notes={'course':self.foundation}
  self.body='### Comprendre la méthode\n\nLe budget aide à anticiper les dépenses puis à comparer les prévisions à la réalisation. '+('Le suivi permet de comprendre les écarts et de prendre des décisions. '*5)+'\n\n### Exemple pédagogique\n\nPour un projet fictif, un coût prévu de 100 euros et un coût réel de 120 euros donnent un dépassement de 20 euros.'
 def tearDown(self):store.DATA=self.old;self.tmp.cleanup()
 def test_knowledge_and_examples_allowed_without_fake_research(self):
  s=store.update(worker.SID,research_enabled=False)
  with patch.object(worker,'teach_answer',return_value=json.dumps({'sections':[{'heading':'Comprendre le budget','body':self.body,'kind':'explanation'}]})):notes=worker.enrich_course(s,self.notes,[{'title':'Budget','scope':'Méthode et exemple'}])
  saved=store.read(worker.SID);self.assertIn('120 euros',notes['course']);self.assertEqual(notes['foundation'],self.foundation);self.assertEqual(saved['research']['status'],'disabled');self.assertNotIn('[00:00]',notes['course']);self.assertTrue(saved['course_complete'])
  evidence=worker.evidence_bank(saved);self.assertTrue(any(e['source_type']=='lesson' for e in evidence.values()))
 def test_real_sources_kept_separate_from_teacher(self):
  source={'status':'ok','sources':[{'id':'R1','title':'Budget','url':'https://fr.wikipedia.org/wiki/Budget','text':'Un budget décrit les recettes et les dépenses prévisionnelles.','provider':'Wikipédia'}]}
  with patch.object(worker,'teach_answer',side_effect=['{"queries":["budget"]}',json.dumps({'sections':[{'heading':'Budget','body':self.body,'kind':'explanation'}]}),json.dumps({'sections':[{'heading':'Budget','body':self.body,'kind':'explanation'}]})]),patch('research.search_topics',return_value=source):worker.enrich_course(self.s,self.notes,[{'title':'Budget','scope':'Méthode et exemple'}])
  saved=store.read(worker.SID);proof=worker.locate_quote({'quote':source['sources'][0]['text'],'source':'R1'},saved);self.assertEqual(proof['source_type'],'research');self.assertIsNone(proof['start']);self.assertEqual(saved['research']['sources'][0]['url'],source['sources'][0]['url'])
 def test_relecture_reports_are_not_lesson_sections(self):
  raw=json.dumps({'sections':[{'heading':'Méthode','body':self.body,'kind':'method'},{'heading':'Clarifications et corrections pédagogiques','body':'Rapport de relecture. '*30,'kind':'explanation'}]})
  rendered=worker.render_teaching_sections(raw);self.assertNotIn('Rapport de relecture',rendered);self.assertIn('Méthode',rendered)
if __name__=='__main__':unittest.main()
