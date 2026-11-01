def test_rfm_skips_future_and_sums():
    from app.domain import rfm_snapshot
    rows=rfm_snapshot([{'customer':'A','date':'2026-01-01','amount':10},{'customer':'A','date':'2027-01-01','amount':100}], '2026-10-22')
    assert rows[0]['orders']==1 and rows[0]['net_value']==10
