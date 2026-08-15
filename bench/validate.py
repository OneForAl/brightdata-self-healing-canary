import json, sys
from pathlib import Path

EXPECTED = [
 {'id':'p-101','name':'Nebula Keyboard','price':2499,'currency':'INR','category':'Keyboards','rating':4.6,'in_stock':True},
 {'id':'p-102','name':'Orbit Mouse','price':1499,'currency':'INR','category':'Mice','rating':4.3,'in_stock':True},
 {'id':'p-103','name':'Quasar Headset','price':3299,'currency':'INR','category':'Audio','rating':4.5,'in_stock':False},
]
REQUIRED = set(EXPECTED[0])

def find_rows(obj):
    if isinstance(obj, list): return obj
    for key in ('data','results','records','items'):
        if isinstance(obj, dict) and isinstance(obj.get(key), list): return obj[key]
    if isinstance(obj, dict) and 'result' in obj: return find_rows(obj['result'])
    return []

def norm(r):
    out = dict(r)
    # tolerate common money representations from an AI-generated scraper
    if isinstance(out.get('price'), dict):
        p=out['price']; out['price']=p.get('value', p.get('amount'))
        out.setdefault('currency', p.get('currency'))
    if isinstance(out.get('price'), str):
        digits=''.join(ch for ch in out['price'] if ch.isdigit())
        out['price']=int(digits) if digits else None
    if isinstance(out.get('rating'), str):
        try: out['rating']=float(out['rating'].split('/')[0].strip())
        except ValueError: pass
    return out

path=Path(sys.argv[1])
obj=json.loads(path.read_text())
rows=find_rows(obj)
if not rows:
    print(json.dumps({'ok':False,'reason':'no rows','row_count':0}, indent=2)); sys.exit(2)
rows=[norm(r) for r in rows]
by_id={str(r.get('id', r.get('product_id', r.get('sku', r.get('ref', ''))))):r for r in rows}
checks=[]
for exp in EXPECTED:
    # match by id, or by name when ID naming differs
    got=by_id.get(exp['id']) or next((r for r in rows if r.get('name')==exp['name']), None)
    checks.append(got == exp)
print(json.dumps({'ok':len(rows)==len(EXPECTED) and all(checks), 'row_count':len(rows), 'row_checks':checks, 'rows':rows}, indent=2))
sys.exit(0 if len(rows)==len(EXPECTED) and all(checks) else 1)
