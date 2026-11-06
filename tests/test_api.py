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
def levels_text(r,title): return next(c['text'] for c in r['checks'] if c['title']==title)
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
    assert r['action']=='Submit course-drop request for CS 440 (Fall 2026)'

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
    assert 'available online yet' in rules.evaluate('graduation',grad['id'],{})['reason']

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

def test_terms_and_key_dates():
    t={x['term']:x for x in rules.terms()}
    assert list(t)==['Fall 2025','Spring 2026','Fall 2026','Winter 2027','Spring 2027','Summer 2027']
    assert (t['Fall 2026']['status'],t['Spring 2027']['status'],t['Fall 2025']['status'])==('current','upcoming','past')
    assert rules.key_dates('GR','Winter 2027')==[] and len(rules.key_dates('UG','Winter 2027'))==6
    assert any(d['label']=='Last day to drop a full semester (POT 1) course without a W' and d['date']=='2027-03-12' for d in rules.key_dates('UG','Spring 2027'))

def test_spring_registration_drop():
    spring=[c['code'] for c in db.get_term_courses(ALEX,'Spring 2027')]
    assert spring and all(c['status']=='Registered' for c in db.get_term_courses(ALEX,'Spring 2027'))
    assert db.get_term_courses(JORDAN,'Spring 2027')==[]  # holds block registration
    r=rules.evaluate('drop',ALEX,{'course_code':'CS 441'},term='Spring 2027')
    assert r['status']=='ready' and levels(r)['Within the deadline to drop without a W']=='ok'
    assert 'Spring 2027 registration' in r['summary']

def test_past_term_drop_blocked():
    code=next(c['code'] for c in db.get_term_courses(ALEX,'Fall 2025'))
    r=rules.evaluate('drop',ALEX,{'course_code':code},term='Fall 2025')
    assert r['status']=='blocked' and 'has ended' in r['summary']

def test_term_endpoints(monkeypatch):
    assert [t['term'] for t in client.get('/api/terms').json()['terms']][2]=='Fall 2026'
    assert client.get(f'/api/students/{ALEX}?term=Spring 2027').json()['term_credits']>0
    assert client.get('/api/students?term=Fall 2031').status_code==404
    monkeypatch.setattr(server,'classify_live',stub('drop',{'course_code':'CS 441'}))
    d=client.post('/api/start',json={'message':'Can I drop CS 441?','student_id':ALEX,'term':'Spring 2027'}).json()
    assert d['state']=='review' and d['term']=='Spring 2027'
    assert client.post('/api/confirm',json={'session_id':d['session_id'],'confirmation':True}).json()['description'].endswith('(Spring 2027)')

def test_normalize_course():
    assert server.normalize_course('CS411','get me out of cs411')=='CS 411'
    assert server.normalize_course('ART 105','drop ART-105?')=='ART 105'
    assert server.normalize_course('CS 411','drop my systems class') is None
    assert server.normalize_course(None,'drop CS 411') is None

def test_student_endpoints():
    assert len(client.get('/api/students').json())==254
    p=client.get(f'/api/students/{ALEX}').json()
    assert p['term_credits']==14 and p['program_name']=='Computer Science, BS'
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
    assert d['state']=='blocked' and 'degree audit is unavailable' in d['result']['reason'].lower()
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

def test_requests_listed_and_duplicates_blocked(monkeypatch):
    sid=find_student(lambda s,cur:s['level']=='UG' and len(db.get_active_holds(s['id']))>0 and s['id']!=JORDAN)['id']
    monkeypatch.setattr(server,'classify_live',stub('hold',{}))
    d=client.post('/api/start',json={'message':"Why can't I register?",'student_id':sid}).json()
    receipt=client.post('/api/confirm',json={'session_id':d['session_id'],'confirmation':True}).json()['receipt']
    reqs=client.get(f'/api/students/{sid}').json()['requests']
    assert [r['receipt'] for r in reqs]==[receipt]
    again=client.post('/api/start',json={'message':"Why can't I register?",'student_id':sid}).json()
    assert again['state']=='blocked'
    assert again['result']['checks'][0]['title']=='You already submitted this request' and receipt in again['result']['checks'][0]['text']

def test_course_search():
    r=rules.evaluate('course_search',JORDAN,{'credits':3,'term':'Spring 2027'},term='Spring 2027')
    assert r['status']=='info' and r['courses']
    assert all(db.get_course(c['code'])['credits_min']<=3<=db.get_course(c['code'])['credits_max'] for c in r['courses'])
    r=rules.evaluate('course_search',ALEX,{'subject':'CS','level':400,'keyword':'learning'},term='Spring 2027')
    assert {c['code'] for c in r['courses']}>={'CS 441','CS 446'} and next(c for c in r['courses'] if c['code']=='CS 441')['record']=='Registered Spring 2027'
    assert 'isn’t available' in rules.evaluate('course_search',ALEX,{},term='Summer 2027')['reason']

def test_course_info():
    r=rules.evaluate('course_info',ALEX,{'course_code':'CS 425'})
    assert r['status']=='info' and 'team project' in levels_text(r,'Counts toward your degree')
    assert rules.evaluate('course_info',ALEX,{'course_code':'CS 999'})['status']=='blocked'

def test_policy_answers_are_quotes():
    r=rules.evaluate('policy',ALEX,{'topic':'full_time'})
    assert levels_text(r,'F-1/J-1 full-time minimum')==db.get_fact('isss_full_time')['quote']
    r=rules.evaluate('policy',ALEX,{'topic':'graduation_application'},term='Spring 2027')
    assert any('February 1, 2027' in c['text'] for c in r['checks'])

def test_clean_entities():
    m='Show me 3 credit IS courses for spring 2027 about data'
    e=server.clean_entities('course_search',{'subject':'is','credits':3,'term':'Spring 2027','keyword':'data','level':450},m)
    assert e=={'subject':'IS','credits':3,'term':'Spring 2027','keyword':'data'}
    assert server.clean_entities('course_search',{'term':'Fall 2026','keyword':'robots'},m)=={'term':'Spring 2027'}  # typed term wins
    assert server.clean_entities('policy',{'topic':'tuition hacks'},'refund?')=={}
    assert server.clean_entities('drop',{'course_code':'CS 411'},'drop CS 411')=={'course_code':'CS 411'}

def test_edge_one_course_at_a_time(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('drop',{'course_code':'CS 411'}))
    d=client.post('/api/start',json={'message':'drop CS 411 and CS 425','student_id':ALEX}).json()
    assert d['state']=='blocked' and 'one course at a time' in d['result']['reason']

def test_edge_unknown_term_in_question(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('course_search',{}))
    d=client.post('/api/start',json={'message':'courses in fall 2030','student_id':ALEX}).json()
    assert d['state']=='blocked' and 'Fall 2030 isn’t available' in d['result']['reason']

def test_edge_numbers_as_text():
    assert server.clean_entities('course_search',{'credits':'3','level':'400'},'3 credit 400 level')=={'credits':3,'level':400}
    assert server.clean_entities('course_search',{'credits':True},'x')=={}

def test_edge_course_in_other_term():
    r=rules.evaluate('drop',ALEX,{'course_code':'CS 441'},term='Fall 2026')
    assert 'on your Spring 2027 registration' in r['reason']

def test_edge_pending_drop_counts(monkeypatch):
    sid=find_student(lambda s,cur:s['level']=='UG' and s['visa'] is None and len(cur)>=4 and not db.list_requests(s['id']))['id']
    a,b=[c['code'] for c in db.get_current(sid)][:2]
    total=sum(c['credits'] for c in db.get_current(sid)); ca=db.get_enrollment(sid,a)['credits']
    db.create_session('edge-1',sid,'drop','Fall 2026',{'course_code':a},'review')
    db.complete_session('edge-1','edge-receipt','drop',{'description':'x','course_code':a})
    r=rules.evaluate('drop',sid,{'course_code':b})
    assert r['metrics'][1]['value']==total-ca and r['checks'][0]['title']=='Includes your pending drop request'
    assert 'already requested to drop' in rules.evaluate('drop',sid,{'course_code':a})['reason']

def test_edge_faults_on_new_question_types():
    assert rules.evaluate('course_info',ALEX,{'course_code':'CS 425'},'missing_record')['status']=='blocked'
    assert rules.evaluate('course_search',ALEX,{'subject':'CS'},'missing_record')['status']=='blocked'
    assert rules.evaluate('policy',ALEX,{'topic':'refunds'},'policy_conflict')['status']=='blocked'

def test_edge_rate_limit_message(monkeypatch):
    class Busy(Exception): status_code=429
    def boom(m): raise Busy()
    monkeypatch.setattr(server,'classify_live',boom)
    r=client.post('/api/start',json={'message':'Can I drop CS 411?','student_id':ALEX})
    assert r.status_code==503 and 'busy' in r.json()['detail']

def test_edge_typed_term_and_multi_drop():
    assert server.clean_entities('drop',{'course_code':'CS 441'},'Can I drop CS 441 in spring 2027?')=={'course_code':'CS 441','term':'Spring 2027'}
    assert 'one course at a time' in server.precheck('unknown','drop CS 411 and CS 425 please')
    assert server.precheck('course_info','compare CS 411 and CS 412') is None

def test_synonyms_in_search():
    r=rules.evaluate('course_search',ALEX,{'subject':'CS','keyword':'ai'},term='Fall 2026')
    assert 'CS 440' in {c['code'] for c in r['courses']}
    r=rules.evaluate('course_search',ALEX,{'subject':'CS','keyword':'databases'},term='Fall 2026')
    assert 'CS 411' in {c['code'] for c in r['courses']}

def test_course_name_resolution():
    e={'course_name':'database class'}
    assert server.resolve_name('drop',ALEX,e,'Fall 2026') is None and e['course_code']=='CS 411'
    e={'course_name':'computer science'}
    assert 'several courses' in server.resolve_name('course_info',ALEX,e,'Fall 2026')
    assert server.clean_entities('drop',{'course_name':'database class'},'can I quit my database class')=={'course_code':None,'course_name':'database class'}

def test_relative_terms_and_short_keywords():
    assert server.typed_terms('what can I take next semester')==['Spring 2027']
    assert server.typed_terms('courses this fall')==['Fall 2026']
    assert 'next fall isn’t available' in server.precheck('course_search','courses next fall')
    assert server.clean_entities('course_search',{'keyword':'AI','term':'Spring 2027'},'any AI courses next spring')=={'keyword':'ai','term':'Spring 2027'}

def test_catalog_extraction_fixes():
    assert db.get_course('CS 464')['credits_text']=='3' and db.get_course('CS 465')['title']=='User Interface Design'
    assert all(len(c['title'])<=80 and 'ﬁ' not in c['title'] for c in db.list_courses())

def test_important_for_student():
    titles=[i['title'] for i in rules.important(JORDAN)]
    assert titles[:2]==['Hold: Immunization requirement','Hold: Financial encumbrance']
    maya=rules.important(MAYA)
    assert maya[0]['title']=='Apply to graduate in December' and not any('Not registered' in i['title'] for i in maya)
    alex=rules.important(ALEX,on=date(2026,11,10))
    assert any(i['urgency']=='urgent' and 'without a W' in i['title'] for i in alex)  # Nov 13 is 3 days away
    assert any(i['title']=='F-1 full-time minimum: 12 hours' for i in alex)

def test_unanswerable_question_points_somewhere(monkeypatch):
    monkeypatch.setattr(server,'classify_live',stub('unknown',{}))
    d=client.post('/api/start',json={'message':'Where is the library?','student_id':JORDAN}).json()
    r=d['result']
    assert r['status']=='info' and r['important'] and any(c['where'] and c['where']['url'] for c in r['checks'])

def test_unverified_items_have_directions():
    sid=find_student(lambda s,cur:s['level']=='UG' and s['visa'] is None and len(cur)>=3)['id']
    r=rules.evaluate('drop',sid,{'course_code':db.get_current(sid)[0]['code']})
    w=next(c['where'] for c in r['checks'] if c['title'].startswith('Drop deadline depends'))
    assert w['url'].startswith('https://courses.illinois.edu/schedule/2026/fall/')


def test_graduation_summary_does_not_guarantee_approval():
    result = rules.evaluate('graduation', MAYA, {})

    summary = result['summary']

    assert 'Graduation is not guaranteed' in summary
    assert '113' in summary
    assert '17' in summary
    assert '130' in summary
    assert '123' in summary
    assert 'graduation has been approved' in summary

    assert result['status'] in ('ready', 'blocked', 'info')
    assert result['action'] is None or result['action'] == 'Save graduation review plan'


def test_hypothetical_course_failure_is_blocked(monkeypatch):
    # Mock the AI classifier so this test is deterministic.
    monkeypatch.setattr(
        server,
        'classify_live',
        stub('graduation', {})
    )

    response = client.post(
        '/api/start',
        json={
            'message': (
                'What if I fail one of my current 3-credit courses? '
                'Will I still be able to graduate in December?'
            ),
            'student_id': MAYA,
            'term': 'Fall 2026'
        }
    )

    assert response.status_code == 200

    data = response.json()
    result = data['result']

    # The hypothetical cannot be treated as a verified audit.
    assert data['intent'] == 'graduation'
    assert result['status'] == 'blocked'
    assert data['state'] == 'blocked'

    # The response explains the unsupported scenario.
    assert 'hypothetical graduation scenario' in result['reason']
    assert 'cannot currently recalculate' in result['reason']

    # No graduation request should be confirmable.
    assert result['action'] is None

    confirmation = client.post(
        '/api/confirm',
        json={
            'session_id': data['session_id'],
            'confirmation': True
        }
    )

    assert confirmation.status_code == 409
    assert db.get_action(data['session_id']) is None
