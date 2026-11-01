"""RetentionLens local development API. NOT FOR CUSTOMER DATA OR PUBLIC EXPOSURE.

Dataset/demo reviewers operate on synthetic records; no authentication or tenant isolation.
"""
import csv
import io
import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .domain import domain_example

APP_NAME = "RetentionLens"
HERE=Path(__file__).resolve()
ROOT=HERE.parents[3]
SAMPLE=ROOT / 'data' / 'sample' / 'demo_cases.csv'
STATE=Path(os.environ.get('DEMO_DB_PATH', str(ROOT / 'services' / 'api' / '.state' / 'demo.sqlite3')))
app=FastAPI(title=APP_NAME+' local starter API',version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
VALID_STATUS={'ready','needs-review','blocked','approved','rejected'}
HEADERS=['id','title','subtitle','metric_value','metric_label','status','evidence']

def connect():
    STATE.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(str(STATE),timeout=20)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA journal_mode = WAL')
    db.execute("CREATE TABLE IF NOT EXISTS demo_records (id TEXT PRIMARY KEY, title TEXT NOT NULL, subtitle TEXT NOT NULL, metric_value TEXT NOT NULL, metric_label TEXT NOT NULL, status TEXT NOT NULL, evidence TEXT NOT NULL, source_type TEXT NOT NULL DEFAULT 'SYNTHETIC')")
    db.execute('CREATE TABLE IF NOT EXISTS demo_reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, record_id TEXT NOT NULL, status TEXT NOT NULL, note TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    return db

def clean_row(row):
    for h in HEADERS:
        if row.get(h) is None or not str(row[h]).strip(): raise ValueError('Missing '+h)
        if len(str(row[h]))>2000: raise ValueError('Field too long: '+h)
    if row['status'] not in VALID_STATUS: raise ValueError('Unsupported status')
    return {k:str(row[k]).strip() for k in HEADERS}

def initialize(db):
    if db.execute('SELECT COUNT(*) FROM demo_records').fetchone()[0]: return
    with SAMPLE.open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            v=clean_row(row)
            db.execute('INSERT INTO demo_records (id,title,subtitle,metric_value,metric_label,status,evidence) VALUES (?,?,?,?,?,?,?)', tuple(v[x] for x in HEADERS))
        db.commit()

class Review(BaseModel):
    record_id: str=Field(min_length=1,max_length=100)
    status: str=Field(pattern='^(ready|needs-review|blocked|approved|rejected)$')
    note: str=Field(min_length=3,max_length=2000)

class CSVImport(BaseModel):
    csv_text:str=Field(min_length=10,max_length=150000)

@app.get('/api/health')
def health():return {'ok':True,'project':APP_NAME,'mode':'LOCAL_SYNTHETIC_DEMO','version':'0.1.0'}

@app.get('/api/demo/records')
def records():
    with connect() as db:
        initialize(db)
        return [dict(x) for x in db.execute('SELECT * FROM demo_records ORDER BY id').fetchall()]

@app.get('/api/demo/summary')
def summary():
    with connect() as db:
        initialize(db)
        rows=db.execute('SELECT status,COUNT(*) n FROM demo_records GROUP BY status').fetchall()
        return {'counts':{r['status']:r['n'] for r in rows},'total':sum(r['n'] for r in rows),'source_type':'SYNTHETIC','note':'Counts of demo review cases, not business KPIs'}

@app.get('/api/demo/domain')
def domain():return domain_example()

@app.post('/api/demo/reviews')
def review(x:Review):
    with connect() as db:
        initialize(db)
        if db.execute('SELECT 1 FROM demo_records WHERE id=?',(x.record_id,)).fetchone() is None: raise HTTPException(404,'Unknown demo record')
        with db:
            db.execute('INSERT INTO demo_reviews (record_id,status,note) VALUES(?,?,?)',(x.record_id,x.status,x.note))
            db.execute('UPDATE demo_records SET status=? WHERE id=?',(x.status,x.record_id))
        return {'ok':True,'record_id':x.record_id,'status':x.status,'source':'SYNTHETIC'}

@app.get('/api/demo/reviews')
def reviews():
    with connect() as db:
        return [dict(x) for x in db.execute('SELECT * FROM demo_reviews ORDER BY id DESC LIMIT 100').fetchall()]

@app.post('/api/demo/import')
def import_demo(x:CSVImport):
    """Local-only sample CSV JSON import; rejects invalid rows atomically, never for PII."""
    try:
        reader=csv.DictReader(io.StringIO(x.csv_text))
        if reader.fieldnames != HEADERS: raise ValueError('CSV headers must exactly match demo template')
        rows=[clean_row(r) for r in reader]
        if not rows: raise ValueError('No rows')
        if len(rows)>250:raise ValueError('Demo limit: 250 rows')
        ids=[r['id'] for r in rows]
        if len(ids)!=len(set(ids)): raise ValueError('Duplicate IDs within upload')
        if any(not i.startswith('D-') for i in ids):raise ValueError('Demo-only IDs must begin D-')
    except (ValueError,csv.Error) as e:raise HTTPException(422,str(e))
    with connect() as db:
        initialize(db)
        with db:
            for r in rows:
                db.execute('INSERT INTO demo_records (id,title,subtitle,metric_value,metric_label,status,evidence) VALUES (?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,subtitle=excluded.subtitle,metric_value=excluded.metric_value,metric_label=excluded.metric_label,status=excluded.status,evidence=excluded.evidence',tuple(r[h] for h in HEADERS))
    return {'ok':True,'upserted':len(rows),'source_type':'SYNTHETIC','note':'Demo-only. This is not a production data importer.'}
