"""Small public encyclopedic research provider. No course files leave the computer."""
import json,re,time
from html.parser import HTMLParser
from urllib.parse import urlencode,quote,urlparse
from urllib.request import Request,urlopen
from datetime import datetime,timezone

USER_AGENT='StudyHUBLocal/5.0 (personal educational research desktop application)'
class ArticleText(HTMLParser):
    def __init__(self):super().__init__();self.depth=0;self.capture=0;self.parts=[];self.current=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('script','style','table','figure','aside','sup'):self.depth+=1
        if tag in ('p','h2','h3') and not self.depth:self.capture+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','table','figure','aside','sup'):self.depth=max(0,self.depth-1)
        if tag in ('p','h2','h3') and self.capture:
            self.capture-=1
            if not self.capture:
                text=' '.join(''.join(self.current).split());self.current=[]
                if text:self.parts.append(text)
    def handle_data(self,text):
        if self.capture and not self.depth:self.current.append(text)
    def text(self):return '\n\n'.join(self.parts)

def public_query(value):
    if not isinstance(value,str):return None
    value=' '.join(value.split()).strip(' "')
    if re.search(r'\b[A-ZÀ-Ý][a-zà-ÿ]+\s+[A-ZÀ-Ý][a-zà-ÿ]+\b',value):return None
    if not 3<=len(value)<=110 or re.search(r'https?://|@|\d{5,}|[<>]',value):return None
    return value

def get(url,json_response=True):
    parsed=urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in ('fr.wikipedia.org','en.wikipedia.org'):raise ValueError('Source de recherche non autorisée')
    with urlopen(Request(url,headers={'User-Agent':USER_AGENT,'Accept':'application/json' if json_response else 'text/html'}),timeout=10) as response:
        if urlparse(response.geturl()).hostname not in ('fr.wikipedia.org','en.wikipedia.org'):raise ValueError('Redirection de recherche refusée')
        payload=response.read(2_000_001)
        if len(payload)>2_000_000:raise ValueError('Article trop volumineux')
    return json.loads(payload) if json_response else payload.decode('utf-8',errors='replace')

def search_topics(queries,language='fr',fetch=get):
    """Bound requests, keep actual URLs and retrieval dates; never invent a source."""
    language='en' if language=='en' else 'fr';sources=[];errors=[];seen=set()
    queries=list(dict.fromkeys(q for value in queries if (q:=public_query(value))))[:3]
    for query in queries:
        try:
            result=fetch(f'https://{language}.wikipedia.org/w/rest.php/v1/search/page?'+urlencode({'q':query,'limit':2}))
            for page in result.get('pages',[])[:2]:
                key=page.get('key');title=page.get('title','')
                if not isinstance(key,str) or key in seen or ':' in key or 'homonymie' in title.lower():continue
                content=fetch(f'https://{language}.wikipedia.org/w/rest.php/v1/page/'+quote(key,safe='')+'/html',False)
                parser=ArticleText();parser.feed(content);text=parser.text()[:9000]
                if len(text)<250:continue
                seen.add(key);sources.append({'id':'R'+str(len(sources)+1),'title':title,'url':f'https://{language}.wikipedia.org/wiki/'+quote(key,safe=''),'text':text,'query':query,'retrieved_at':datetime.now(timezone.utc).isoformat(),'provider':'Wikipédia','license':'CC BY-SA — voir l’article et son historique'})
                break
        except Exception as error:errors.append({'query':query,'error':type(error).__name__})
    return {'status':'ok' if sources else 'unavailable','provider':'Wikipédia','queries':queries,'sources':sources,'errors':errors}
