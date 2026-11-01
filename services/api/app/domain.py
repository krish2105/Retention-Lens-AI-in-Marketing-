from datetime import date

def rfm_snapshot(invoices: list[dict], as_of: str) -> list[dict]:
    """Demo RFM descriptive summary; no churn probabilities or causal recommendations."""
    cutoff=date.fromisoformat(as_of); acc={}
    for i in invoices:
        d=date.fromisoformat(i['date'])
        if d>cutoff:continue
        key=i['customer']; s=acc.setdefault(key,{'customer':key,'last_date':None,'orders':0,'net_value':0.0})
        s['orders']+=1; s['net_value']+=float(i['amount'])
        if s['last_date'] is None or d>s['last_date']:s['last_date']=d
    return [{**s,'recency_days':(cutoff-s['last_date']).days,'last_date':s['last_date'].isoformat()} for s in acc.values() if s['last_date']]

def domain_example():
    d=[{'customer':'A','date':'2026-09-01','amount':100},{'customer':'A','date':'2026-10-01','amount':120},{'customer':'B','date':'2026-10-10','amount':85}]
    return {'method':'descriptive RFM only, not trained purchase model', 'accounts':rfm_snapshot(d,'2026-10-22'),'source':'SYNTHETIC customer transactions'}
