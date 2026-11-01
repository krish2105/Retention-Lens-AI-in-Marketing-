def test_health(client):
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['mode']=='LOCAL_SYNTHETIC_DEMO'

def test_seed_summary(client):
    records=client.get('/api/demo/records').json()
    summary=client.get('/api/demo/summary').json()
    assert len(records)==3 and summary['total']==3
    assert all(x['source_type']=='SYNTHETIC' for x in records)

def test_review_updates_status_and_history(client):
    rows=client.get('/api/demo/records').json(); record_id=rows[0]['id']
    r=client.post('/api/demo/reviews',json={'record_id':record_id,'status':'approved','note':'Demo-only review'})
    assert r.status_code==200
    assert next(x for x in client.get('/api/demo/records').json() if x['id']==record_id)['status']=='approved'
    assert client.get('/api/demo/reviews').json()[0]['note']=='Demo-only review'

def test_import_bad_header_and_duplicate_are_rejected(client):
    assert client.post('/api/demo/import',json={'csv_text':'a,b\n1,2'}).status_code==422
    hdr='id,title,subtitle,metric_value,metric_label,status,evidence\n'
    row='D-TEST,X,Y,12,items,ready,DEMO\n'
    assert client.post('/api/demo/import',json={'csv_text':hdr+row+row}).status_code==422

def test_domain_has_synthetic_provenance(client):
    assert 'SYNTHETIC' in str(client.get('/api/demo/domain').json())
