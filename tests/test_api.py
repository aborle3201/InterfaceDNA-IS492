import sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import pytest
from fastapi.testclient import TestClient
import db
import generate_students
import rules
import server
client=TestClient(server.app)
ALEX,MAYA,JORDAN,SAM='S00001','S00002','S00003','S00004'
CS411={'course_code':'CS 411'}
DURING_TERM=date(2026,11,5)

@pytest.fixture(scope='session',autouse=True)
def fresh_db(tmp_path_factory):
    db.DB_PATH=tmp_path_factory.mktemp('db')/'test.db'
    db.reset()

@pytest.fixture(autouse=True)
def term_date(monkeypatch):
    monkeypatch.setenv('INTERFACEDNA_TODAY',DURING_TERM.isoformat())

def stub(intent,entities):
    return lambda message:(intent,entities,'stub',{'model':'test-stub','input_tokens':1,'output_tokens':1})

def levels(r): return {c['title']:c['level'] for c in r['checks']}
def level_of(r,prefix): return next(c['level'] for c in r['checks'] if c['title'].startswith(prefix))
def blockers(r): return [c['title'] for c in r['checks'] if c['blocks']]

def find_student(pred):
    for s in db.list_students():
        full=db.get_student(s['id'])
        if pred(full,db.get_current(s['id'])): return full
    raise AssertionError('no matching synthetic student')

def test_real_course_data():
    c=db.get_course('CS 411')
    assert (c['title'],c['credits_text'],c['source_document'])==('Database Systems','3 or 4','CS courses.pdf')
    assert db.get_fact('isss_full_time')['values']=={'UG':12,'GR':8}

def test_generator_is_deterministic_and_valid():
    a,b=generate_students.generate(),generate_students.generate()
    assert a==b and len(a)==254
    courses=generate_students.load_courses()
    scheduled,offered=generate_students.load_offered()
    for s in a:
        for e in s['enrollments']:
            c=courses[e['code']]
            assert c['credits_min']<=e['credits']<=c['credits_max']
            if e['status']=='Enrolled' and e['code'].split()[0] in scheduled:
                assert e['code'] in offered

def test_featured_students():
    assert db.get_student(ALEX)['visa']=='F-1'
    assert sum(c['credits'] for c in db.get_current(ALEX))==14
    assert db.get_student(MAYA)['visa'] is None
    assert len(db.get_active_holds(JORDAN))==2

def test_drop_f1_below_full_time_blocks():
    r=rules.evaluate('drop',ALEX,CS411)
    assert r['status']=='blocked' and r['action'] is None
    assert level_of(r,'Contact ISSS before dropping below full time')=='block'
    assert level_of(r,'Drop deadline depends on')=='unknown'
    assert level_of(r,'Tuition range changes from Range I to Range II, but no refund')=='info'
    assert {'isss_full_time','isss_before_dropping','f26_oct_16','f26_nov_13'}<={s['key'] for s in r['sources']}

def test_drop_requires_enrolled_named_course():
    assert 'does not include CS 500' in rules.evaluate('drop',ALEX,{'course_code':'CS 500'})['reason']
    assert rules.evaluate('drop',ALEX,{'course_code':None})['status']=='blocked'

def test_drop_domestic_has_no_visa_check():
    s=find_student(lambda s,cur:s['level']=='UG' and s['visa'] is None and len(cur)>=3)
    r=rules.evaluate('drop',s['id'],{'course_code':db.get_current(s['id'])[0]['code']})
    assert not any('ISSS' in c['title'] or 'visa' in c['title'] for c in r['checks'])
    assert len(blockers(r))==1 and blockers(r)[0].startswith('Drop deadline depends on')

def test_drop_only_course_is_withdrawal():
    s=find_student(lambda s,cur:len(cur)==1)
    r=rules.evaluate('drop',s['id'],{'course_code':db.get_current(s['id'])[0]['code']})
    assert levels(r)['Dropping your only course is a withdrawal']=='block'

def test_ug_no_w_deadlines_by_date():
    for on,expected in [(date(2026,9,1),'ok'),(date(2026,10,20),'unknown'),(date(2026,11,14),'block')]:
        r=rules.evaluate('drop',ALEX,CS411,on=on)
        assert [c['level'] for c in r['checks'] if 'without a W' in c['title'] or 'part of term' in c['title']]==[expected],on

def test_grad_drop_within_deadline_is_ready():
    r=rules.evaluate('drop',SAM,{'course_code':'CS 440'})
    assert r['status']=='ready' and levels(r)['Within the deadline to drop without a W']=='ok'
    assert r['action']=='Submit synthetic course-drop request for CS 440'

def test_grad_petition_after_dec_10():
    title='Graduate add/drop now requires a petition'
    assert title not in levels(rules.evaluate('drop',SAM,{'course_code':'CS 440'},on=date(2026,12,10)))
    assert levels(rules.evaluate('drop',SAM,{'course_code':'CS 440'},on=date(2026,12,11)))[title]=='block'

def test_graduation():
    maya=rules.evaluate('graduation',MAYA,{})
    assert maya['status']=='ready'
    assert [c['title'] for c in maya['checks'] if c['level']=='warn']==['Apply to graduate in December']
    alex=rules.evaluate('graduation',ALEX,{})
    assert levels(alex)['CS 374']=='info' and levels(alex)['CS 421']=='warn'
    grad=find_student(lambda s,cur:s['level']=='GR')
    assert 'not supported' in rules.evaluate('graduation',grad['id'],{})['reason']

def test_holds():
    r=rules.evaluate('hold',JORDAN,{})
    assert r['status']=='ready' and levels(r)['Immunization requirement']=='warn'
    assert 'open registration begins November 19, 2026' in next(c['text'] for c in r['checks'] if c['title']=='Spring 2027 registration dates')
    assert rules.evaluate('hold',ALEX,{})['status']=='info'

def test_failures_block():
    for intent,sid,ent,fault in [('drop',ALEX,CS411,'policy_conflict'),('graduation',MAYA,{},'missing_record'),('hold',JORDAN,{},'service_outage'),('drop',ALEX,CS411,'missing_record'),('hold',JORDAN,{},'missing_record')]:
        assert rules.evaluate(intent,sid,ent,fault)['status']=='blocked'

def test_every_student_and_journey_is_cited():
    for s in db.list_students():
        cur=db.get_current(s['id'])
        for intent,ent in [('drop',{'course_code':cur[0]['code'] if cur else None}),('graduation',{}),('hold',{})]:
            r=rules.evaluate(intent,s['id'],ent)
            assert r['status'] in ('ready','blocked','info')
            keys={x['key'] for x in r['sources']}
            for c in r['checks']:
                assert set(c['cites'])<=keys
            assert all(x['quote'] for x in r['sources'])

def test_normalize_course():
    assert server.normalize_course('CS411','get me out of cs411')=='CS 411'
    assert server.normalize_course('ART 105','drop ART-105?')=='ART 105'
    assert server.normalize_course('CS 411','drop my systems class') is None
    assert server.normalize_course(None,'drop CS 411') is None

def test_student_endpoints():
    assert len(client.get('/api/students').json())==254
    p=client.get(f'/api/students/{ALEX}').json()
    assert p['current_credits']==14 and p['program_name']=='Computer Science, BS'
    assert client.get('/api/students/S99999').status_code==404

def test_confirm_flow(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('hold',{}))
    d=client.post('/api/start',json={'message':"Why can't I register?",'student_id':JORDAN}).json()
    sid=d['session_id']
    assert d['state']=='review'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':False}).status_code==400
    assert client.post('/api/fault',json={'session_id':sid,'mode':'service_outage'}).json()['state']=='blocked'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
    assert client.post('/api/fault',json={'session_id':sid,'mode':'none'}).json()['state']=='review'
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).json()['synthetic'] is True
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).status_code==409
    assert db.get_action(sid)['action_type']=='hold'

def test_maya_missing_audit_recovery(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('graduation',{}))
    sid=client.post('/api/start',json={'message':'What do I still need to graduate?','student_id':MAYA}).json()['session_id']
    d=client.post('/api/fault',json={'session_id':sid,'mode':'missing_record'}).json()
    assert d['state']=='blocked' and 'degree audit is unavailable' in d['result']['reason']
    r=client.post('/api/confirm',json={'session_id':sid,'confirmation':True})
    assert r.status_code==409 and 'receipt' not in r.json()
    assert db.get_action(sid) is None
    d=client.post('/api/fault',json={'session_id':sid,'mode':'none'}).json()
    assert d['state']=='review' and any(c['title']=='IS 101' for c in d['result']['checks'])
    assert client.post('/api/confirm',json={'session_id':sid,'confirmation':True}).json()['state']=='completed'

def test_grad_drop_confirm(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('drop',{'course_code':'CS 440'}))
    d=client.post('/api/start',json={'message':'Can I drop CS 440?','student_id':SAM}).json()
    assert d['state']=='review'
    assert client.post('/api/confirm',json={'session_id':d['session_id'],'confirmation':True}).json()['state']=='completed'
    monkeypatch.setenv('INTERFACEDNA_TODAY','2026-12-11')
    d=client.post('/api/start',json={'message':'Can I drop CS 412?','student_id':SAM}).json()
    assert d['state']=='blocked'

def test_unverified_drop_cannot_be_confirmed(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('drop',CS411))
    d=client.post('/api/start',json={'message':'Can I drop CS 411?','student_id':ALEX}).json()
    assert d['state']=='blocked'
    assert client.post('/api/confirm',json={'session_id':d['session_id'],'confirmation':True}).status_code==409
    assert db.get_action(d['session_id']) is None

def test_model_failure_creates_no_session(monkeypatch):
    def boom(message): raise RuntimeError('no key')
    monkeypatch.setattr(server,'classify_live',boom)
    assert client.post('/api/start',json={'message':'Can I drop CS 411?','student_id':ALEX}).status_code==503
