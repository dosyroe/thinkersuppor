from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import json
import re
import unicodedata

out=Path(r'D:\DemoExam\analysis')
def load(name):
    return json.loads((out/(name+'_import.json')).read_text(encoding='utf-8'))[0]['rows'][1:]
def norm(v):
    return ' '.join(unicodedata.normalize('NFKC', str(v)).split())
def key(name, manufacturer):
    return norm(name), norm(manufacturer)
products,users,sizes,stock,orders=[load(n) for n in ['Products','Users','Sizes','Stock_Items','Orders']]
product_by_key={key(r['values'][3],r['values'][4]):r for r in products}
aliases={('Черные туфли в классическом стиле','Барбари'):('Черные туфли в классическом стиле — база для деловых образов','Барбари')}
issues=[]
raw_keys={(r['values'][3],r['values'][4]) for r in products}
inventory=defaultdict(int)
stock_keys=set()
for r in stock:
    name,manufacturer,size,qty=r['values']
    k=key(name,manufacturer)
    target=aliases.get(k,k)
    if (name,manufacturer) not in raw_keys:
        issues.append({'file':'Stock_Items','row':r['row'],'kind':'model_name_mismatch','source':name,'target':target[0] if target in product_by_key else None})
    if target not in product_by_key:
        raise ValueError(f'Unmapped stock {r}')
    if (target,Decimal(str(size))) in stock_keys:
        issues.append({'file':'Stock_Items','row':r['row'],'kind':'duplicate_model_size'})
    stock_keys.add((target,Decimal(str(size))))
    inventory[target]+=qty
user_by_fio={' '.join(norm(v) for v in r['values'][:3]):r for r in users}
order_groups=defaultdict(list)
for r in orders:
    oid,dt,fio,category,name,manufacturer,size,qty,price=r['values']
    k=key(name,manufacturer)
    target=aliases.get(k,k)
    if (name,manufacturer) not in raw_keys:
        issues.append({'file':'Orders','row':r['row'],'kind':'model_name_mismatch','source':name,'target':target[0] if target in product_by_key else None})
    if target not in product_by_key: raise ValueError(f'Unmapped order {r}')
    if norm(fio) not in user_by_fio: issues.append({'file':'Orders','row':r['row'],'kind':'unknown_client','fio':fio})
    if (target,Decimal(str(size))) not in stock_keys: issues.append({'file':'Orders','row':r['row'],'kind':'unknown_stock_item'})
    if category!=product_by_key[target]['values'][0]: issues.append({'file':'Orders','row':r['row'],'kind':'category_mismatch'})
    if price!=product_by_key[target]['values'][7]: issues.append({'file':'Orders','row':r['row'],'kind':'historical_price_diff','historical':price,'current':product_by_key[target]['values'][7]})
    order_groups[oid].append(r)
for oid,rows in order_groups.items():
    headers={(r['values'][1],r['values'][2]) for r in rows}
    if len(headers)!=1: issues.append({'order':oid,'kind':'conflicting_order_header'})
assets=Path(r'D:\DemoExam\КИМ_ДЭ_09.02.07-2\Прил_ОЗ_КИМ_09.02.07-2-2027\Прил_2_ОЗ_КИМ_09.02.07-2-2027\Images')
report={
    'counts':{'files':len(json.loads((out/'inventory.json').read_text(encoding='utf-8'))),'products':len(products),'sizes':len(sizes),'users':len(users),'stock_items':len(stock),'orders':len(order_groups),'order_lines':len(orders),'available_pairs':sum(inventory.values()),'ordered_pairs':sum(r['values'][7] for r in orders)},
    'categories':dict(Counter(r['values'][0] for r in products)),
    'roles':dict(Counter(r['values'][4] for r in users)),
    'issues':issues,
    'low_stock_models':[{'name':k[0],'manufacturer':k[1],'quantity':v} for k,v in inventory.items() if v<=3],
    'missing_images':[r['values'][2] for r in products if not (assets/r['values'][2]).exists()],
    'orders_by_month':dict(Counter(r['values'][1][:7] for rows in order_groups.values() for r in rows[:1])),
    'orders':[{'id':oid,'date':rows[0]['values'][1][:10],'lines':len(rows),'pairs':sum(r['values'][7] for r in rows),'total':sum(r['values'][7]*r['values'][8] for r in rows)} for oid,rows in order_groups.items()],
    'special_characters': [{'file':'Products','row':r['row'],'column':c+1,'character':'NBSP' if '\u00a0' in v else 'outer_whitespace','value':v} for r in products for c,v in enumerate(r['values']) if isinstance(v,str) and ('\u00a0' in v or v.strip()!=v)],
    'user_latin_in_name':[{'row':r['row'],'name':r['values'][:3]} for r in users if any(re.search('[A-Za-z]',v) for v in r['values'][:3])],
    'duplicate_logins':[v for v,c in Counter(r['values'][3] for r in users).items() if c>1]
}
(out/'data_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Audit saved to analysis/data_audit.json')
