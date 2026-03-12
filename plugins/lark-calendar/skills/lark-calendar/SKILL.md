---
name: lark-calendar
description: LarkSuite calendar management - events, attendees, scheduling. Use when user asks about calendar, meetings, or scheduling. Requires lark-token-manager MCP.
---

# Lark Calendar

Manage LarkSuite calendar events, attendees, and scheduling.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app with `calendar:calendar` scope

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` to get:
- `linked_users[].lark_open_id` -> user_open_id
- `linked_users[].lark_user_id` -> user_id (for attendees)
- `linked_users[].primary_calendar_id` -> calendar_id

### Step 2: Get access token from MCP

Call MCP `get_lark_token(app_name=LARK_APP_NAME)`
- If expired: MCP `refresh_lark_token` -> if fails: MCP `start_oauth`

### Step 3: Initialize client

```python
import subprocess
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-calendar/scripts/", "/home/claude/"])

import sys
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkCalendarClient
from utils import get_today_range_ms, datetime_to_calendar_timestamp, get_default_reminder

client = LarkCalendarClient(
    access_token=TOKEN_FROM_MCP,
    user_open_id=OPEN_ID_FROM_WHOAMI,
    user_id=USER_ID_FROM_WHOAMI
)
```

## API Methods

| Method | Description |
|--------|-------------|
| `list_events(cal_id, start_ms, end_ms)` | List events in a time range. Accepts milliseconds and converts to seconds internally. Returns list of event dicts with `event_id`, `summary`, `start_time`, `end_time`, `status`. Use `get_today_range_ms()` for convenience. |
| `create_event(cal_id, event_data)` | Create calendar event. Auto-adds creator as attendee if `user_id` set on client. Requires `start_time` and `end_time` (seconds timestamps). Supports `summary`, `description` (HTML ok), `visibility`, `free_busy_status`, `reminders`, `recurrence` (RRULE), `vchat`, `location`. See api-reference.md for all fields. |
| `add_event_attendees(cal_id, event_id, attendees)` | Add attendees to existing event. Attendee format: `[{"type": "user", "user_id": "lark_user_id"}]`. Types: `user`, `chat`, `resource` (room), `third_party` (email). Max 1000 per request, 3000 total per event. |
| `update_event(cal_id, event_id, data)` | Partial update — only fields in data dict are changed. Organizers can update all fields; invitees limited to `visibility`, `free_busy_status`, `color`, `reminders`. Updating time requires both `start_time` and `end_time`. |
| `delete_event(cal_id, event_id)` | Delete event permanently. Only the event organizer can delete. Returns `bool`. Sends attendee notification by default. |

## Timestamp Rules

> **Calendar API** uses **SECONDS** (10 digits): `"1704067200"`

- `datetime_to_calendar_timestamp(dt)` -> seconds string (use for event start/end)
- `list_events()` accepts milliseconds and converts internally

## Quick Examples

### View today's calendar
```python
start_ms, end_ms = get_today_range_ms()
events = client.list_events(calendar_id, start_ms, end_ms)
```

### Create event with attendee
```python
from datetime import datetime, timedelta
tomorrow_14 = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)

event = client.create_event(calendar_id, {
    "summary": "Team Meeting",
    "start_time": {"timestamp": datetime_to_calendar_timestamp(tomorrow_14)},
    "end_time": {"timestamp": datetime_to_calendar_timestamp(tomorrow_14 + timedelta(hours=1))},
    "description": "Location: Meeting Room A",
    "reminders": [get_default_reminder()]
})
client.add_event_attendees(calendar_id, event["event_id"], [
    {"type": "user", "user_id": "lark_user_id_from_mcp"}
])
```

## Defaults

- **Event Duration**: 1 hour (if end_time not specified, calculate manually)
- **Reminder**: 30 minutes before (`get_default_reminder()`)
- **Visibility**: `default` (follows calendar setting)

## Personnel Lookup

Use MCP `search_users` tool directly -- no Python needed:
```
MCP search_users(query="Huong") -> [{name, email, department, lark_user_id, ...}]
```
Use `lark_user_id` for Calendar attendees.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, required/optional fields, return types
- [api-examples.md](./references/api-examples.md) — Realistic code samples (recurring, all-day, video conf)
- [api-validation.md](./references/api-validation.md) — Full enums, schemas, error codes, rate limits
