import sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import pytest
from fastapi.testclient import TestClient
import db
import rules
import server
client=TestClient(server.app)
BEFORE,ON,AFTER=date(2026,9,15),date(2026,9,30),date(2026,10,1)
CS411={'course_code':'CS 411'}

@pytest.fixture(autouse=True)
def fresh_db(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'test.db')
    monkeypatch.setenv('INTERFACEDNA_TODAY',BEFORE.isoformat())
    db.reset()

def stub(intent,entities):
    return lambda message:(intent,entities,'stub',{'model':'test-stub','input_tokens':1,'output_tokens':1})

def test_seeded_records():
    assert db.get_student('alex')['name']=='Alex Morgan'
    assert db.current_credits('alex')==16
    assert db.current_credits('jordan')==14
    assert db.get_enrollment('alex','CS 411')['credits']==4
    assert db.get_enrollment('alex','CS 500') is None

def test_credit_math():
    r=rules.evaluate('drop','alex',CS411,on=BEFORE)
    assert r['details']['before_credits']==16
    assert r['details']['after_credits']==12
    assert r['details']['below_threshold'] is False

def test_drop_uses_requested_course():
    r=rules.evaluate('drop','alex',{'course_code':'CS 425'},on=BEFORE)
    assert r['details']['course_code']=='CS 425'
    assert r['action'].endswith('CS 425')
    assert rules.evaluate('drop','alex',{'course_code':'CS 500'},on=BEFORE)['status']=='blocked'
    assert rules.evaluate('drop','alex',{'course_code':None},on=BEFORE)['status']=='blocked'

def test_drop_deadline():
    assert rules.evaluate('drop','alex',CS411,on=BEFORE)['status']=='ready'
    assert rules.evaluate('drop','alex',CS411,on=ON)['status']=='ready'
    late=rules.evaluate('drop','alex',CS411,on=AFTER)
    assert late['status']=='blocked' and 'deadline' in late['reason']

def test_graduation_and_holds():
    assert rules.evaluate('graduation','maya',{})['details']['remaining_if_in_progress_pass']==0
    assert len(rules.evaluate('hold','jordan',{})['details']['holds'])==2
    assert rules.evaluate('graduation','alex',{})['status']=='blocked'

def test_failures_block():
    for intent,persona,ent,fault in [('drop','alex',CS411,'policy_conflict'),('graduation','maya',{},'missing_record'),('hold','jordan',{},'service_outage'),('drop','alex',CS411,'missing_record'),('hold','jordan',{},'missing_record')]:
        assert rules.evaluate(intent,persona,ent,fault)['status']=='blocked'

def test_conflict_shows_both_sources():
    r=rules.evaluate('drop','alex',CS411,'policy_conflict')
    assert [s['date'] for s in r['sources']]==['September 25, 2026','September 30, 2026']

def test_normalize_course():
    assert server.normalize_course('CS411','get me out of cs411')=='CS 411'
    assert server.normalize_course('ART 105','drop ART-105?')=='ART 105'
    assert server.normalize_course('CS 411','drop my systems class') is None
    assert server.normalize_course(None,'drop CS 411') is None

def test_live_model_path_mocked(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('drop',CS411))
    d=client.post('/api/start',json={'message':'Can I drop CS 411?','persona':'alex'}).json()
    sid=d['session_id']
    assert d['state']=='review' and d['entities']==CS411
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':False}).status_code==400
    assert client.post('/api/fault',json={'session_id':sid,'mode':'policy_conflict'}).json()['state']=='blocked'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
    assert client.post('/api/fault',json={'session_id':sid,'mode':'none'}).json()['state']=='review'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).json()['synthetic'] is True
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
    assert db.get_session(sid)['state']=='completed'
    assert db.get_action(sid)['details']['course_code']=='CS 411'

def test_confirm_rechecks_deadline(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('drop',CS411))
    sid=client.post('/api/start',json={'message':'Can I drop CS 411?','persona':'alex'}).json()['session_id']
    monkeypatch.setenv('INTERFACEDNA_TODAY',AFTER.isoformat())
    r=client.post('/api/confirm',json={'session_id':sid,'confirmation':True})
    assert r.status_code==409 and 'deadline' in r.json()['detail']
    assert db.get_action(sid) is None

def test_model_failure_creates_no_session(monkeypatch):
    def boom(message): raise RuntimeError('no key')
    monkeypatch.setattr(server,'classify_live',boom)
    assert client.post('/api/start',json={'message':'Can I drop CS 411?','persona':'alex'}).status_code==503
