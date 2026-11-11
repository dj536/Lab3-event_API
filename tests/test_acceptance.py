"""Acceptance tests for Lab 3 - Campus Events API. Do not modify.

    pip install -r requirements.txt
    pytest tests -q
"""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TODAY = date.today()


def make_event(title="AI Night", days=7, capacity=2):
    payload = {"title": title, "date": (TODAY + timedelta(days=days)).isoformat(), "capacity": capacity}
    response = client.post("/events", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_event_returns_201_and_counters():
    event = make_event(capacity=3)
    assert isinstance(event["id"], int)
    assert event["registered"] == 0
    assert event["seats_left"] == 3


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "AI Night", "date": "2030-01-01", "capacity": 0},
        {"title": "AI Night", "date": "2030-01-01", "capacity": -5},
        {"title": "AI", "date": "2030-01-01", "capacity": 10},
        {"title": "AI Night", "date": "not-a-date", "capacity": 10},
        {"title": "AI Night", "capacity": 10},
    ],
)
def test_create_event_validation(payload):
    assert client.post("/events", json=payload).status_code == 422


def test_get_event_and_404():
    event = make_event()
    assert client.get(f"/events/{event['id']}").json()["title"] == "AI Night"
    assert client.get("/events/999999").status_code == 404


def test_list_sorted_by_date():
    later = make_event(title="Later event", days=30)
    sooner = make_event(title="Sooner event", days=3)
    ids = [e["id"] for e in client.get("/events").json()]
    assert ids.index(sooner["id"]) < ids.index(later["id"])


def test_upcoming_filter_excludes_past_events():
    past = make_event(title="Past event", days=-10)
    future = make_event(title="Future event", days=10)
    ids = [e["id"] for e in client.get("/events", params={"upcoming": "true"}).json()]
    assert future["id"] in ids
    assert past["id"] not in ids


def test_register_updates_counters():
    event = make_event(capacity=2)
    response = client.post(f"/events/{event['id']}/registrations", json={"email": "ana@school.fr"})
    assert response.status_code == 201
    assert response.json() == {"event_id": event["id"], "email": "ana@school.fr"}
    refreshed = client.get(f"/events/{event['id']}").json()
    assert refreshed["registered"] == 1
    assert refreshed["seats_left"] == 1


def test_register_full_event_returns_409():
    event = make_event(capacity=1)
    assert client.post(f"/events/{event['id']}/registrations", json={"email": "a@x.com"}).status_code == 201
    assert client.post(f"/events/{event['id']}/registrations", json={"email": "b@x.com"}).status_code == 409


def test_duplicate_email_is_case_insensitive():
    event = make_event(capacity=5)
    assert client.post(f"/events/{event['id']}/registrations", json={"email": "Ana@X.com"}).status_code == 201
    assert client.post(f"/events/{event['id']}/registrations", json={"email": "ana@x.com"}).status_code == 409


@pytest.mark.parametrize("email", ["not-an-email", "ana@", "@x.com", "ana@xcom"])
def test_register_invalid_email(email):
    event = make_event()
    assert client.post(f"/events/{event['id']}/registrations", json={"email": email}).status_code == 422


def test_register_unknown_event_returns_404():
    assert client.post("/events/999999/registrations", json={"email": "a@x.com"}).status_code == 404


def test_unregister():
    event = make_event(capacity=1)
    client.post(f"/events/{event['id']}/registrations", json={"email": "a@x.com"})
    assert client.delete(f"/events/{event['id']}/registrations/a@x.com").status_code == 204
    assert client.get(f"/events/{event['id']}").json()["seats_left"] == 1
    assert client.delete(f"/events/{event['id']}/registrations/a@x.com").status_code == 404
