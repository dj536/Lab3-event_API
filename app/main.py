"""Campus Events API - build it with Copilot Agent mode, following SPEC.md."""
from datetime import date

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Campus Events API")

events: dict[int, dict[str, int | str | date]] = {}
registrations: dict[int, dict[str, str]] = {}
next_event_id = 1


class EventCreate(BaseModel):
	title: str = Field(min_length=3, max_length=80)
	date: date
	capacity: int = Field(gt=0)


class RegistrationCreate(BaseModel):
	email: str


@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate) -> dict[str, int | str | date]:
	global next_event_id

	event_id = next_event_id
	next_event_id += 1
	created_event: dict[str, int | str | date] = {
		"id": event_id,
		"title": event.title,
		"date": event.date,
		"capacity": event.capacity,
		"registered": 0,
		"seats_left": event.capacity,
	}
	events[event_id] = created_event
	registrations[event_id] = {}
	return created_event


@app.get("/events")
def list_events(upcoming: bool = False) -> list[dict[str, int | str | date]]:
	today = date.today()
	matching_events = [
		event
		for event in events.values()
		if not upcoming or event["date"] >= today
	]
	return sorted(matching_events, key=lambda event: event["date"])


@app.get("/events/{event_id}")
def get_event(event_id: int) -> dict[str, int | str | date]:
	event = events.get(event_id)
	if event is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
	return event


@app.post(
	"/events/{event_id}/registrations",
	status_code=status.HTTP_201_CREATED,
)
def create_registration(
	event_id: int, registration: RegistrationCreate
) -> dict[str, int | str]:
	email = registration.email
	local_and_domain = email.split("@")
	if len(local_and_domain) != 2 or not local_and_domain[0] or "." not in local_and_domain[1]:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail="Invalid email",
		)

	event = events.get(event_id)
	if event is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
	if event["registered"] >= event["capacity"]:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Event is full")

	normalized_email = email.casefold()
	event_registrations = registrations[event_id]
	if normalized_email in event_registrations:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Email already registered",
		)

	event_registrations[normalized_email] = email
	event["registered"] = int(event["registered"]) + 1
	event["seats_left"] = int(event["capacity"]) - int(event["registered"])
	return {"event_id": event_id, "email": email}


@app.delete(
	"/events/{event_id}/registrations/{email}",
	status_code=status.HTTP_204_NO_CONTENT,
)
def delete_registration(event_id: int, email: str) -> None:
	event = events.get(event_id)
	if event is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

	event_registrations = registrations[event_id]
	normalized_email = email.casefold()
	if normalized_email not in event_registrations:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Registration not found",
		)

	del event_registrations[normalized_email]
	event["registered"] = int(event["registered"]) - 1
	event["seats_left"] = int(event["capacity"]) - int(event["registered"])
