---
name: lark-docs
description: "LarkSuite document creation and block-level editing via DocX API.
Use when user asks about document, doc, docs, write document, create doc, add text,
add heading, block, paragraph, todo list in doc, read document content.
Requires lark-token-manager MCP."
---

# Lark Docs

Create and edit LarkSuite documents: create docs, add text/headings/todos,
read content, update blocks, and manage document structure via DocX block tree.

## Prerequisites

- `lark-token-manager` MCP server configured
- Lark app scopes: `docx:document` (read+write), `docx:document:readonly` (read only)

## Initialization

### Step 1: Get user info
MCP `whoami` -> `linked_users[].lark_open_id` -> user_open_id

### Step 2: Get token
MCP `get_lark_token(app_name)` -> ACCESS_TOKEN
- If expired: MCP `refresh_lark_token` -> if fails: MCP `start_oauth`

### Step 3: Init client
```python
import subprocess
subprocess.run(["cp", "-r", "/mnt/skills/user/lark-docs/scripts/", "/home/claude/"])

import sys
sys.path.insert(0, '/home/claude/scripts')

from lark_api import LarkDocsClient

client = LarkDocsClient(access_token=ACCESS_TOKEN, user_open_id=OPEN_ID)
```

## Decision Guide

```
Create new document?               -> client.create_document(title, folder_token)
Get document info?                 -> client.get_document(document_id)
Read plain text content?           -> client.get_raw_content(document_id)
List all blocks in doc?            -> client.list_blocks(document_id)

Get a specific block?              -> client.get_block(document_id, block_id)
Get children of a block?           -> client.get_block_children(document_id, block_id)
Add blocks to document?            -> client.create_blocks(document_id, parent_id, children)
Update block content?              -> client.update_block(document_id, block_id, ...)
Batch update multiple blocks?      -> client.batch_update_blocks(document_id, requests)
Delete blocks by index?            -> client.delete_blocks(document_id, parent_id, start, end)

Quick add text?                    -> client.create_text_block(document_id, parent_id, text)
Quick add heading?                 -> client.create_heading_block(document_id, parent_id, text, level)
Quick add todo?                    -> client.create_todo_block(document_id, parent_id, text, done)
```

## API Methods (13 total)

### Document (4)
| Method | Description |
|--------|-------------|
| `create_document(title=None, folder_token=None)` | Create doc, returns `{document: {document_id, revision_id, title}}` |
| `get_document(document_id)` | Get metadata (document_id, revision_id, title) |
| `get_raw_content(document_id, lang=0)` | Plain text content. lang: 0=all, 1=zh, 2=en, 3=ja |
| `list_blocks(document_id)` | All blocks in doc tree (paginated, auto-fetches) |

### Block (6)
| Method | Description |
|--------|-------------|
| `get_block(document_id, block_id)` | Single block with content |
| `get_block_children(document_id, block_id)` | Direct children (paginated) |
| `create_blocks(document_id, block_id, children, index=None)` | Create 1-50 child blocks under parent |
| `update_block(document_id, block_id, update_text_elements=None, ...)` | Update block content (one op type per call) |
| `batch_update_blocks(document_id, requests)` | Batch update up to 200 blocks |
| `delete_blocks(document_id, block_id, start_index, end_index)` | Delete children by index range [start, end) |

### Convenience (3)
| Method | Description |
|--------|-------------|
| `create_text_block(document_id, parent_block_id, text, bold, italic)` | Quick text block |
| `create_heading_block(document_id, parent_block_id, text, level=1)` | Heading level 1-9 |
| `create_todo_block(document_id, parent_block_id, text, done=False)` | Todo/checklist block |

## Key Constraints

- **Service path is `docx`** (not `docs`): all URLs use `/open-apis/docx/v1/`
- **Block tree model**: documents are trees of typed blocks; page block_id == document_id
- **No delete document API** in DocX — use Drive API (see Cross-Domain below)
- **Write rate limit**: 3 edits/sec per document (create, update, batch_update, delete blocks)
- **Read rate limit**: 5 reads/sec per app
- **`delete_blocks` uses index range** [start, end) on parent's children, NOT block IDs
- **`create_blocks` limit**: 1-50 children per call
- **`batch_update_blocks` limit**: max 200 requests per call
- **Timestamps**: MILLISECONDS (13 digits) for Reminder elements

## Cross-Domain Operations

**Delete document**: `DELETE /open-apis/drive/v1/files/{document_id}?type=docx`
**Share document**: `POST /open-apis/drive/v1/permissions/{document_id}/members` with `{member_type, member_id, perm}`
**Move document**: `POST /open-apis/drive/v1/files/{document_id}/move` with `{type: "docx", folder_token}`

These use the same ACCESS_TOKEN. Activate `lark-drive` skill for full Drive operations.

## Personnel Lookup

Use MCP `search_users` tool directly -- no Python needed:
```
MCP search_users(query="Name") -> [{name, email, department, lark_open_id, ...}]
```
Use `lark_open_id` for sharing with `member_type="openid"`.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 99991663 | Token expired | `refresh_lark_token` via MCP |
| 1254290 | Rate limited | Backoff (2s, 4s, 8s) |
| 1770001 | Invalid param | Check request body |
| 1770002 | Not found | Document may be deleted |
| 1770032 | Forbidden | Check document permissions |
| 1770039 | Folder not found | Check folder_token |

## References

- [api-reference.md](./references/api-reference.md) — Full method params, return types
- [api-examples.md](./references/api-examples.md) — Code samples for common scenarios
- [api-validation.md](./references/api-validation.md) — Block types, constraints, error codes
