---
name: lark-task
description: LarkSuite task management - tasks, subtasks, tasklists, sections, custom fields. Use when user asks about tasks, todos, project tracking, or work items. Requires lark-token-manager MCP.
---

# Lark Task

Manage LarkSuite tasks, subtasks, tasklists, sections, and custom fields.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app with `task:task:write`, `task:tasklist:write`, `task:section:write`, `task:custom_field:write` scopes

## Initialization

### Step 1: Get user info from MCP

Call MCP `whoami` to get:
- `linked_users[].lark_open_id` -> user_open_id

### Step 2: Get access token from MCP

Call MCP `get_lark_token(app_name=LARK_APP_NAME)`
- If expired: MCP `refresh_lark_token` → if fails: MCP `start_oauth`

### Step 3: Initialize client

```python
import subprocess
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-task/scripts/", "/home/claude/"])

import sys
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkTaskClient
from utils import datetime_to_task_timestamp, is_task_completed, get_today_range_ms

client = LarkTaskClient(
    access_token=TOKEN_FROM_MCP,
    user_open_id=OPEN_ID_FROM_WHOAMI
)
```

## API Methods

### Tasks
| Method | Description |
|--------|-------------|
| `list_tasks(completed=None)` | List "my_tasks" (owned tasks). `completed=False` for pending only, `True` for completed, `None` for all. Returns tasks in custom UI order. |
| `create_task(task_data)` | Create task. Auto-assigns to current user if no `members`. Requires `summary` (max 3000 chars). Supports `due` (ms timestamp), `members` (`[{id, type, role}]`), `reminders` (max 1, needs `due`), `tasklists`, `repeat_rule`, `client_token` for idempotency. Rate limit: 10/sec. |
| `get_task(guid)` | Get full task details including members, reminders, and custom field values. |
| `update_task(guid, data)` | Partial update using `{"task": {...}, "update_fields": ["field_name"]}` pattern. Only listed fields are changed. Manage members/reminders via separate APIs. |
| `delete_task(guid)` | Permanently delete task. Cannot be recovered. |

### Subtasks
| Method | Description |
|--------|-------------|
| `list_subtasks(task_guid)` | List all subtasks of a parent task. Returns same structure as tasks. |
| `create_subtask(task_guid, data)` | Create subtask under parent. Same fields as create_task; `summary` required. Requires edit permission on parent. Rate limit: 10/sec. |

### Tasklists
| Method | Description |
|--------|-------------|
| `list_tasklists()` | List all tasklists the user has access to. Returns `[{guid, name, members}]`. |
| `create_tasklist(name, members=None)` | Create tasklist. `name` required (max 100 chars). Creator becomes owner automatically. Add members as `[{id, type, role}]` with roles: `editor` or `viewer`. |
| `delete_tasklist(guid)` | Delete tasklist without deleting its tasks. |
| `get_tasklist_tasks(guid, completed=None)` | Get all tasks in a tasklist. Use `is_task_completed(t)` to check status. |

### Sections
| Method | Description |
|--------|-------------|
| `list_sections(resource_type, resource_id=None)` | List sections for `"tasklist"` (provide GUID) or `"my_tasks"`. Returns list with `guid`, `name`, `is_default` in UI order. |
| `create_section(name, resource_type, resource_id=None)` | Create section. `name` required (max 100 chars). Optional `insert_before`/`insert_after` for positioning (mutually exclusive). |
| `get_section(guid)` | Get section details. |
| `update_section(guid, name=None)` | Update section name. |
| `delete_section(guid)` | Delete section; tasks move to default section. |
| `list_section_tasks(guid, completed=None)` | List tasks within a section. |

### Custom Fields
| Method | Description |
|--------|-------------|
| `list_custom_fields(resource_type=None, resource_id=None)` | List custom fields for a resource. |
| `create_custom_field(name, type, resource_type, resource_id)` | Create and attach field to tasklist. `type`: `number`\|`member`\|`datetime`\|`single_select`\|`multi_select`\|`text`. Pass type-specific settings dict. Rate: 100/min. |
| `get_custom_field(guid)` | Get field details including options for select types. |
| `update_custom_field(guid, name=None, settings=None)` | Update field name or settings. |
| `add_custom_field_to_resource(guid, type, id)` | Link existing field to another tasklist. |
| `remove_custom_field_from_resource(guid, type, id)` | Unlink field from a tasklist. |

## Timestamp Rules

> **Task API** uses **MILLISECONDS** (13 digits): `"1704067200000"`

- `datetime_to_task_timestamp(dt)` -> milliseconds string
- `completed_at`: String `"0"` = not done, ms string = done

## Quick Examples

### Create task with deadline
```python
from datetime import datetime, timedelta
friday = (datetime.now() + timedelta(days=3)).replace(hour=17, minute=0, second=0, microsecond=0)
task = client.create_task({
    "summary": "Fix login bug",
    "due": {"timestamp": datetime_to_task_timestamp(friday), "is_all_day": False}
})
```

### Create workflow sections
```python
for name in ["Backlog", "In Progress", "Review", "Done"]:
    client.create_section(name=name, resource_type="tasklist", resource_id=tasklist_guid)
```

### Check progress
```python
all_tasks = client.get_tasklist_tasks(tasklist_guid)
done = [t for t in all_tasks if is_task_completed(t)]
print(f"Progress: {len(done)}/{len(all_tasks)} ({len(done)*100//len(all_tasks)}%)")
```

## Personnel Lookup

Use MCP `search_users` tool directly -- no Python needed:
```
MCP search_users(query="Huong") -> [{name, email, department, lark_open_id, ...}]
```
Use `lark_open_id` for Task members.

## References

- [api-reference.md](./references/api-reference.md) — Full method params, required/optional fields, return types
- [api-examples.md](./references/api-examples.md) — Code samples (kanban setup, custom fields, full workflow)
- [api-validation.md](./references/api-validation.md) — Member format, due format, custom field schemas, error codes
