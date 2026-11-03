"""Render worked numerical examples with computed arithmetic, not model-supplied totals."""
import ast,math,re
from decimal import Decimal,InvalidOperation

def calculate(expression,values):
    if not isinstance(expression,str) or len(expression)>160:raise ValueError('Expression invalide')
    def visit(node):
        if isinstance(node,ast.Expression):return visit(node.body)
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):return Decimal(str(node.value))
        if isinstance(node,ast.Name) and node.id in values:return Decimal(str(values[node.id]))
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):return visit(node.operand)*(1 if isinstance(node.op,ast.UAdd) else -1)
        if isinstance(node,ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if isinstance(node.op,ast.Div) and b:return a/b
        raise ValueError('Calcul non pris en charge')
    result=visit(ast.parse(expression,mode='eval'))
    if not result.is_finite() or abs(result)>Decimal('1e20'):raise ValueError('Résultat invalide')
    return result

def display(value):return format(Decimal(str(value)).normalize(),'f').replace('.',',')

def worked_example(section):
    context=section.get('context','');interpretation=section.get('interpretation','')
    rows=section.get('values',[]);steps=section.get('calculations',[])
    if not isinstance(context,str) or not isinstance(interpretation,str) or re.search(r'\d',context+interpretation):raise ValueError('Les valeurs doivent être séparées du texte')
    if not isinstance(rows,list) or not isinstance(steps,list) or not rows or not steps:raise ValueError('Exemple chiffré incomplet')
    values={};lines=[context]
    for row in rows[:8]:
        name=row.get('name','');value=row.get('value');label=row.get('label','')
        if not re.fullmatch(r'[a-zA-Z][a-zA-Z_]{0,24}',name) or type(value) not in (int,float) or not math.isfinite(value) or not isinstance(label,str):raise ValueError('Valeur pédagogique invalide')
        if name in values:raise ValueError('Variable répétée')
        values[name]=value;lines.append('- '+label+' : '+display(value)+' '+str(row.get('unit',''))[:15]+'.')
    for step in steps[:6]:
        result=calculate(step.get('expression'),values)
        formula=re.sub(r'\b[a-zA-Z_]+\b',lambda match:display(values[match[0]]) if match[0] in values else match[0],step['expression'])
        lines.append('- '+str(step.get('label','Calcul'))+' : '+formula+' = **'+display(result)+' '+str(step.get('unit',''))[:15]+'**.')
    if interpretation:lines.append(interpretation)
    return '\n\n'.join(lines)

def budget_example():
    return worked_example({'context':'Exemple fictif : une équipe prépare un événement. Les montants prévus et réels ci-dessous portent sur les mêmes dépenses et la même période.','values':[{'name':'prevu','label':'Coût prévu','value':10000,'unit':'€'},{'name':'reel','label':'Coût réel','value':11500,'unit':'€'}],'calculations':[{'label':'Écart de coût, avec la convention réel moins prévu','expression':'reel - prevu','unit':'€'},{'label':'Écart rapporté au coût prévu','expression':'(reel - prevu) / prevu * 100','unit':'%'}],'interpretation':'Avec cette convention, un résultat positif signifie que les dépenses réelles dépassent la prévision. Il faut ensuite chercher la cause de cet écart avant de décider d’une adaptation. Ce pourcentage décrit uniquement cet exemple ; ce n’est pas une règle de marge à appliquer à tous les projets.'})

def ensure_example(text,topic):
    if 'exemple pédagogique' in text.lower():return text
    if re.search(r'budget|coût|prévisionnel',topic,re.I):return text+'\n\n### Exemple pédagogique · lire un écart de coût\n\n'+budget_example()
    return text
