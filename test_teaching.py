import unittest
from teaching import calculate,worked_example,ensure_example
class TeachingTests(unittest.TestCase):
 def test_arithmetic_is_computed(self):
  self.assertEqual(calculate('reel - prevu',{'reel':95000,'prevu':80000}),15000)
  self.assertEqual(calculate('(reel - prevu) / prevu * 100',{'reel':120,'prevu':100}),20)
 def test_budget_example_is_consistent_and_not_duplicated(self):
  body=ensure_example('Explication du budget de projet.','Budget de projet');self.assertIn('**1500 €**',body);self.assertIn('**15 %**',body);self.assertEqual(ensure_example(body,'Budget'),body)
 def test_no_code_execution(self):
  for expression in ["__import__('os').system('echo nope')",'x.y','[1][0]','1/0']:
   with self.assertRaises((ValueError,ArithmeticError)):calculate(expression,{})
 def test_model_result_is_ignored(self):
  example={'context':'Un projet fictif compare deux coûts.','values':[{'name':'prevu','label':'Coût prévu','value':100},{'name':'reel','label':'Coût réel','value':120}],'calculations':[{'label':'Écart','expression':'reel-prevu','result':900}],'interpretation':'Le montant réel dépasse le montant prévu.'}
  text=worked_example(example);self.assertIn('**20 ',text);self.assertNotIn('900',text)
if __name__=='__main__':unittest.main()
