import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from fastapi.testclient import TestClient
import server
client=TestClient(server.app)

def test_credit_math():
    r=server.facts('drop','alex')
    assert r['details']['before_credits']==16
    assert r['details']['after_credits']==12
    assert r['details']['below_threshold'] is False

def test_graduation_and_holds():
    assert server.facts('graduation','maya')['details']['remaining_if_in_progress_pass']==0
    assert len(server.facts('hold','jordan')['details']['holds'])==2

def test_failures_block():
    for intent,persona,fault in [('drop','alex','policy_conflict'),('graduation','maya','missing_record'),('hold','jordan','service_outage')]:
        assert server.facts(intent,persona,fault)['status']=='blocked'

def test_live_model_path_mocked(monkeypatch):
    monkeypatch.setattr(server,'classify_live',lambda message:('drop','Drop request',{'model':'test-stub','input_tokens':1,'output_tokens':1}))
    d=client.post('/api/start',json={'message':'Can I drop CS 411?','persona':'alex'}).json()
    sid=d['session_id']
    assert d['state']=='review'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':False}).status_code==400
    assert client.post('/api/fault',json={'session_id':sid,'mode':'policy_conflict'}).json()['state']=='blocked'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
    assert client.post('/api/fault',json={'session_id':sid,'mode':'none'}).json()['state']=='review'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).json()['synthetic'] is True
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
