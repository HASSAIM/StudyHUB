import unittest
from research import search_topics,ArticleText,public_query
class ResearchTests(unittest.TestCase):
 def test_only_concepts_and_actual_sources(self):
  seen=[]
  def fetch(url,json_response=True):
   seen.append(url)
   if json_response:return {'pages':[{'key':'Budget','title':'Budget'}]}
   return '<h2>Définition</h2><p>Le budget regroupe les recettes et les dépenses. '+('Un suivi compare les montants prévus et réalisés. '*12)+'</p><script>FAUSSE_INSTRUCTION</script>'
  result=search_topics(['budget','a@b.fr','https://private.test','budget'],fetch=fetch)
  self.assertEqual(result['status'],'ok');self.assertEqual(len(result['sources']),1);self.assertEqual(result['sources'][0]['url'],'https://fr.wikipedia.org/wiki/Budget');self.assertNotIn('FAUSSE_INSTRUCTION',result['sources'][0]['text']);self.assertEqual(len(seen),2)
 def test_outage_is_reported_without_invented_source(self):
  def fail(*args):raise OSError('offline')
  result=search_topics(['budget'],fetch=fail);self.assertEqual(result['status'],'unavailable');self.assertEqual(result['sources'],[])
 def test_private_looking_query_is_refused(self):
  self.assertIsNone(public_query('personne@example.com'));self.assertIsNone(public_query('0612345678'));self.assertIsNone(public_query('Marie Dupont'))
if __name__=='__main__':unittest.main()
