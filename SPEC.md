# SPEC — Campus Events API (Lab 3)

## Context
Students' associations want a tiny API to publish events and let students register.
Stack: Python 3.11+, FastAPI, in-memory storage (a dict is fine), pytest.
The FastAPI object must be importable as `from app.main import app`.

## Data
- **Event**: `id` (int, auto), `title` (str, 3–80 chars), `date` (ISO date `YYYY-MM-DD`), `capacity` (int > 0)
- **Registration**: `email` (must contain one `@` and a `.` after it), linked to an event

## Endpoints
| Method | Path | Success | Errors |
|---|---|---|---|
| POST | `/events` body `{title, date, capacity}` | **201** + event JSON with `id`, `registered` (0), `seats_left` | **422** invalid body |
| GET | `/events` | **200** list of events, sorted by date ascending | — |
| GET | `/events?upcoming=true` | **200** only events with `date >= today` | — |
| GET | `/events/{id}` | **200** event JSON incl. `registered` and `seats_left` | **404** unknown id |
| POST | `/events/{id}/registrations` body `{email}` | **201** `{event_id, email}` | **404** unknown event · **409** event full · **409** email already registered · **422** invalid email |
| DELETE | `/events/{id}/registrations/{email}` | **204** | **404** unknown event or email not registered |

## Rules
- Emails are compared case-insensitively (`Ana@X.com` == `ana@x.com`).
- `seats_left = capacity - registered`.

## Definition of Done
1. `pytest tests -q` → all acceptance tests green (provided by the instructor).
2. At least **5 tests of your own** in `tests/test_mine.py`.
3. `.github/copilot-instructions.md` written **before** coding.
4. At least **5 small commits** with meaningful messages.
