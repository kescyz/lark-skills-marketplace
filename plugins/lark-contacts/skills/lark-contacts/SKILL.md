---
name: lark-contacts
description: "LarkSuite contacts - people search, org chart, department hierarchy, user groups.
Use when user asks about employees, departments, org chart, people lookup, team members,
who is in a department, find someone. Uses tenant_access_token (app-level). Org admins only. Requires lark-token-manager MCP."
---

# Lark Contacts

Single entry point for all people and org queries. Hybrid: MCP cache for fast lookups, live API for rich data.

## Prerequisites

- `lark-token-manager` MCP server configured in `.mcp.json`
- `LARK_SKILL_API_KEY` exported before launching Claude Code
- Lark app scopes: `contact:contact:readonly_as_app`, `contact:user.base:readonly`, `contact:user.department:readonly`, `contact:user.email:readonly`, `contact:user.employee:readonly`, `contact:user.employee_id:readonly`, `contact:group:readonly`, `contact:user.id:readonly`
- **Org admin status** (enforced by MCP `get_tenant_token`)

## Initialization

### Step 1: Get user info and verify admin status
Call MCP `whoami` → check `is_admin: true` → get `linked_users[].lark_open_id` → user_open_id
- If `is_admin: false`: inform user that org admin access is required for Contacts API

### Step 2: Get TENANT token from MCP (NOT get_lark_token)
MCP `get_tenant_token(app_name)` → TENANT_TOKEN (requires org admin)

### Step 3: Init client
```python
import subprocess
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-contacts/scripts/", "/home/claude/"])

import sys
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkContactsClient
from utils import format_user_summary, format_department_tree, format_org_chart

client = LarkContactsClient(
    access_token=TENANT_TOKEN,
    user_open_id=OPEN_ID,
)
```

## Decision Guide

```
Need to find someone by name/email?   → MCP search_users(query=...) — fast, <100ms, no Python
Need full profile (30+ fields)?       → client.get_user(open_id)
Need everyone in a department?        → client.list_department_members(dept_id)
Need org chart / dept tree?           → client.get_org_chart(dept_id="0", fetch_child=True)
Need to resolve emails → Lark IDs?   → client.batch_resolve_ids(emails=[...])
Need dept ancestry path?              → client.get_department_path(dept_id)
Need to search depts by keyword?      → MCP search_users(query=...) or browse via get_org_chart
Need user groups?                     → client.list_groups() / client.list_group_members(group_id)
```

## Personnel Lookup

```python
# Quick: MCP (no Python needed)
MCP search_users(query="Minh") → [{name, email, department, lark_open_id, ...}]

# Deep: full 30+ field profile
user = client.get_user(open_id_from_mcp)

# Combo: full profile from email in one call
user = client.get_user_by_email("minh@company.com")
```

## API Methods

### People

| Method | Description |
|--------|-------------|
| `get_user(user_id, id_type="open_id")` | Full profile: name, email, job_title, dept, status, city, join_time, custom_attrs |
| `list_department_members(dept_id, page_size=50)` | All users in dept, paginated. Root dept = "0" |
| `get_user_by_email(email)` | Email → batch_resolve_ids → get_user. Returns None if not found |
| `batch_resolve_ids(emails, mobiles, include_resigned=False)` | Resolve up to 50 emails + 50 mobiles → open_ids |

### Departments

| Method | Description |
|--------|-------------|
| `get_department(dept_id, id_type="department_id")` | Dept info: name, leader, member_count, chat_id |
| `get_org_chart(dept_id="0", fetch_child=False, page_size=50)` | Children of dept. fetch_child=True for full recursive tree |
| `get_department_path(dept_id, id_type="department_id")` | Ancestor chain from dept to root |

### Groups

| Method | Description |
|--------|-------------|
| `list_groups(page_size=100)` | All user groups in company |
| `get_group(group_id)` | Group detail: name, description, type, member_count |
| `list_group_members(group_id, member_id_type="open_id")` | All members of a group |

## Cross-Skill Integration

```python
# Get open_ids for department → pass to messenger/calendar/task
members = client.list_department_members("od-engineering")
open_ids = [u["open_id"] for u in members]

# Resolve email list → open_ids for batch messaging
result = client.batch_resolve_ids(emails=["a@co.com", "b@co.com"])
open_ids = [u["user_id"] for u in result.get("user_list", [])]
```

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types
- [api-examples.md](./references/api-examples.md) — Code samples (org chart, batch resolve, cross-skill)
- [api-validation.md](./references/api-validation.md) — Scopes→fields, rate limits, constraints, error codes
