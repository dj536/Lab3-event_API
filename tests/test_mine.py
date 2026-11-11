"""Additional integration tests for the Campus Events API."""
from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_event(*, days_from_today: int = 7, capacity: int = 2) -> dict:
    token = uuid4().hex
    response = client.post(
        "/events",
        json={
            "title": f"Test {token}",
            "date": (date.today() + timedelta(days=days_from_today)).isoformat(),
            "capacity": capacity,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_event_with_invalid_capacity_returns_422() -> None:
    response = client.post(
        "/events",
        json={
            "title": f"Invalid capacity {uuid4().hex}",
            "date": date.today().isoformat(),
            "capacity": 0,
        },
    )

    assert response.status_code == 422


def test_event_list_is_sorted_and_upcoming_filter_excludes_past_events() -> None:
    past_event = create_event(days_from_today=-2)
    future_event = create_event(days_from_today=5)

    all_events = client.get("/events")
    assert all_events.status_code == 200
    all_ids = [event["id"] for event in all_events.json()]
    assert all_ids.index(past_event["id"]) < all_ids.index(future_event["id"])

    upcoming_events = client.get("/events", params={"upcoming": "true"})
    assert upcoming_events.status_code == 200
    upcoming_ids = [event["id"] for event in upcoming_events.json()]
    assert past_event["id"] not in upcoming_ids
    assert future_event["id"] in upcoming_ids


def test_get_unknown_event_returns_404() -> None:
    response = client.get("/events/-1")

    assert response.status_code == 404


def test_duplicate_registration_is_case_insensitive() -> None:
    event = create_event(capacity=3)
    email = f"student-{uuid4().hex}@example.com"

    first_response = client.post(
        f"/events/{event['id']}/registrations", json={"email": email}
    )
    duplicate_response = client.post(
        f"/events/{event['id']}/registrations", json={"email": email.upper()}
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_unregister_frees_capacity_for_a_new_registration() -> None:
    event = create_event(capacity=1)
    first_email = f"first-{uuid4().hex}@example.com"
    next_email = f"next-{uuid4().hex}@example.com"

    assert client.post(
        f"/events/{event['id']}/registrations", json={"email": first_email}
    ).status_code == 201
    assert client.post(
        f"/events/{event['id']}/registrations", json={"email": next_email}
    ).status_code == 409

    delete_response = client.delete(
        f"/events/{event['id']}/registrations/{first_email.upper()}"
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    freed_event = client.get(f"/events/{event['id']}").json()
    assert freed_event["registered"] == 0
    assert freed_event["seats_left"] == 1
    assert client.post(
        f"/events/{event['id']}/registrations", json={"email": next_email}
    ).status_code == 201
