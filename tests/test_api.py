from fastapi.testclient import TestClient
import copy
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


# Ensure each test runs with a fresh copy of the in-memory activities
import pytest

@pytest.fixture(autouse=True)
def reset_activities():
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure the test email is not present initially
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant added via GET
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    data = resp2.json()
    assert email in data[activity]["participants"]

    # Unregister the participant
    resp3 = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert "Unregistered" in body3.get("message", "")

    # Verify removed
    resp4 = client.get("/activities")
    assert resp4.status_code == 200
    data2 = resp4.json()
    assert email not in data2[activity]["participants"]


def test_unregister_nonexistent_participant():
    activity = "Chess Club"
    email = "noone@nowhere.example"

    # Ensure the email is not in participants
    assert email not in activities[activity]["participants"]

    # Attempt to delete -> should return 404
    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp.status_code == 404
    body = resp.json()
    assert "Participant not found" in body.get("detail", "")
