import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
from fastapi.testclient import TestClient
import server
client=TestClient(server.app)


def test_credit_math(monkeypatch):
    from datetime import date

    # Use a fictional pre-deadline date.
    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 9, 29)
    )

    r = server.facts('drop', 'alex')

    assert r['status'] == 'ready'
    assert r['details']['before_credits'] == 16
    assert r['details']['after_credits'] == 12
    assert r['details']['below_threshold'] is False

def test_graduation_and_holds():
    assert server.facts('graduation','maya')['details']['remaining_if_in_progress_pass']==0
    assert len(server.facts('hold','jordan')['details']['holds'])==2

def test_failures_block():
    for intent,persona,fault in [('drop','alex','policy_conflict'),('graduation','maya','missing_record'),('hold','jordan','service_outage')]:
        assert server.facts(intent,persona,fault)['status']=='blocked'


def test_live_model_path_mocked(monkeypatch):
    from datetime import date

    # Simulate a valid date before the synthetic course-drop deadline.
    monkeypatch.setattr(
        server,
        'policy_today',
        lambda: date(2026, 9, 29)
    )

    # Mock the live LLM response for deterministic API testing.
    monkeypatch.setattr(
        server,
        'classify_live',
        lambda message: (
            'drop',
            'Drop request',
            {
                'model': 'test-stub',
                'input_tokens': 1,
                'output_tokens': 1
            }
        )
    )



def test_drop_before_deadline(monkeypatch):
    from datetime import date

    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 9, 29)
    )

    result = server.facts('drop', 'alex')

    assert result['status'] == 'ready'
    assert result['details']['after_credits'] == 12


def test_drop_on_deadline(monkeypatch):
    from datetime import date

    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 9, 30)
    )

    result = server.facts('drop', 'alex')

    # The synthetic deadline is inclusive.
    assert result['status'] == 'ready'


def test_drop_after_deadline(monkeypatch):
    from datetime import date

    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 10, 1)
    )

    result = server.facts('drop', 'alex')

    assert result['status'] == 'blocked'
    assert result['details']['deadline_passed'] is True
    assert 'September 30, 2026' in result['reason']


def test_confirmation_rechecks_deadline(monkeypatch):
    from datetime import date

    # Mock the LLM classifier, not the backend policy checks.
    monkeypatch.setattr(
        server,
        'classify_live',
        lambda message: (
            'drop',
            'Course drop requested',
            {
                'model': 'test-stub',
                'input_tokens': 1,
                'output_tokens': 1
            }
        )
    )

    # Start the session before the deadline.
    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 9, 29)
    )

    response = client.post(
        '/api/start',
        json={
            'message': 'Can I drop CS 411?',
            'persona': 'alex'
        }
    )

    assert response.status_code == 200
    assert response.json()['state'] == 'review'

    session_id = response.json()['session_id']

    # Simulate the deadline passing before confirmation.
    monkeypatch.setattr(
        server, 'policy_today',
        lambda: date(2026, 10, 1)
    )

    confirmation = client.post(
        '/api/confirm',
        json={
            'session_id': session_id,
            'confirmation': True
        }
    )

    # The server must block the action without issuing a receipt.
    assert confirmation.status_code == 409
    assert 'receipt' not in confirmation.json()


def test_maya_missing_audit_recovery(monkeypatch):
    # Mock only AI classification.
    # The real backend session and validation logic remain active.
    monkeypatch.setattr(
        server,
        "classify_live",
        lambda message: (
            "graduation",
            "Graduation requirements requested",
            {
                "model": "test-stub",
                "input_tokens": 1,
                "output_tokens": 1
            }
        )
    )

    # 1. Start a normal Maya session.
    response = client.post(
        "/api/start",
        json={
            "message": "What do I still need to graduate?",
            "persona": "maya"
        }
    )

    assert response.status_code == 200
    assert response.json()["state"] == "review"

    session_id = response.json()["session_id"]

    # 2. Inject a missing degree audit.
    blocked = client.post(
        "/api/fault",
        json={
            "session_id": session_id,
            "mode": "missing_record"
        }
    )

    assert blocked.status_code == 200
    assert blocked.json()["state"] == "blocked"
    assert blocked.json()["result"]["status"] == "blocked"

    # 3. Try confirming while blocked.
    denied = client.post(
        "/api/confirm",
        json={
            "session_id": session_id,
            "confirmation": True
        }
    )

    assert denied.status_code == 409
    assert "receipt" not in denied.json()

    # 4. Restore normal operation.
    restored = client.post(
        "/api/fault",
        json={
            "session_id": session_id,
            "mode": "none"
        }
    )

    assert restored.status_code == 200
    assert restored.json()["state"] == "review"
    assert restored.json()["result"]["status"] == "ready"

    # 5. Confirm only after recovery.
    confirmed = client.post(
        "/api/confirm",
        json={
            "session_id": session_id,
            "confirmation": True
        }
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["synthetic"] is True
    assert confirmed.json()["receipt"]


def test_jordan_service_outage_recovery(monkeypatch):
    # Simulate the LLM recognizing a registration-hold request.
    monkeypatch.setattr(
        server,
        "classify_live",
        lambda message: (
            "hold",
            "Registration hold request",
            {
                "model": "test-stub",
                "input_tokens": 1,
                "output_tokens": 1
            }
        )
    )

    # 1. Start Jordan's normal session.
    response = client.post(
        "/api/start",
        json={
            "message": "Why can't I register?",
            "persona": "jordan"
        }
    )

    assert response.status_code == 200
    assert response.json()["state"] == "review"

    session_id = response.json()["session_id"]

    # 2. Simulate a records-service outage.
    blocked = client.post(
        "/api/fault",
        json={
            "session_id": session_id,
            "mode": "service_outage"
        }
    )

    assert blocked.status_code == 200
    assert blocked.json()["state"] == "blocked"

    # 3. The backend must reject confirmation.
    denied = client.post(
        "/api/confirm",
        json={
            "session_id": session_id,
            "confirmation": True
        }
    )

    assert denied.status_code == 409
    assert "receipt" not in denied.json()

    # 4. Clear the injected outage.
    restored = client.post(
        "/api/fault",
        json={
            "session_id": session_id,
            "mode": "none"
        }
    )

    assert restored.status_code == 200
    assert restored.json()["state"] == "review"

    holds = restored.json()["result"]["details"]["holds"]

    # Both verified synthetic holds must return.
    assert len(holds) == 2
    assert holds[0]["office"] == "Academic Advising"
    assert holds[1]["office"] == "Student Accounts"

    # 5. The recovered session can now be confirmed.
    confirmed = client.post(
        "/api/confirm",
        json={
            "session_id": session_id,
            "confirmation": True
        }
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["synthetic"] is True
    assert confirmed.json()["receipt"]

