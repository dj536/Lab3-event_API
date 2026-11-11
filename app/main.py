"""Campus Events API - build it with Copilot Agent mode, following SPEC.md."""
from datetime import date

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Campus Events API")

events: dict[int, dict[str, int | str | date]] = {}
next_event_id = 1


class EventCreate(BaseModel):
	title: str = Field(min_length=3, max_length=80)
	date: date
	capacity: int = Field(gt=0)


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
