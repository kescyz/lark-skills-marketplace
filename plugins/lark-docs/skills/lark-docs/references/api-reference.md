# Lark Docs API Reference

> Token management handled by `lark-token-manager` MCP server.
> See [api-examples.md](./api-examples.md) for code samples.
> See [api-validation.md](./api-validation.md) for block types, schemas, error codes.

## LarkDocsClient

```python
from lark_api import LarkDocsClient
client = LarkDocsClient(access_token="u-xxx", user_open_id="ou_xxx")
```

## Contents

- [Document Operations](#document-operations)
- [Block Operations](#block-operations)
- [Convenience Helpers](#convenience-helpers)
- [Rate Limits](#rate-limits)
- [Error Codes](#error-codes)

---

## Document Operations

### create_document(title, folder_token)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| title | str | No | Document title | 1-800 chars |
| folder_token | str | No | Target folder | Empty = root dir |

**Returns**: `{"document": {"document_id": str, "revision_id": int, "title": str}}`

### get_document(document_id)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | 27 chars |

**Returns**: `{"document": {"document_id": str, "revision_id": int, "title": str}}`

### get_raw_content(document_id, lang)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| lang | int | No | Language filter | 0=all, 1=zh, 2=en, 3=ja |

**Returns**: `{"content": str}` — plain text of document

### list_blocks(document_id, page_size)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| page_size | int | No | Items per page | Max 500 (default) |

**Returns**: `List[block]` — all blocks, auto-paginates via `_fetch_all`

---

## Block Operations

### get_block(document_id, block_id)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Block ID | — |

**Returns**: `{"block": {block_type, block_id, children_ids, parent_id, ...}}`

### get_block_children(document_id, block_id, page_size)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | — |
| page_size | int | No | Items per page | Max 500 (default) |

**Returns**: `List[block]` — direct children, auto-paginates

### create_blocks(document_id, block_id, children, index)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | Use document_id for root |
| children | list | **Yes** | Block objects to create | 1-50 items |
| index | int | No | Insert position | None = append |

Auto-sets `document_revision_id=-1` (latest version).

**Returns**: `{"children": [block, ...], "document_revision_id": int, "client_token": str}`

### update_block(document_id, block_id, update_text_elements, update_table_property, update_text_style)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Block to update | — |
| update_text_elements | dict | No | `{"elements": [...]}` | 1+ elements |
| update_table_property | dict | No | Table property changes | — |
| update_text_style | dict | No | Text style changes | — |

Pass only ONE operation type per call.

**Returns**: `{"block": {updated_block}, "document_revision_id": int}`

### batch_update_blocks(document_id, requests)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| requests | list | **Yes** | Update requests | Max 200 items |

Each request: `{"block_id": str, "update_text_elements": {"elements": [...]}}`

**Returns**: `{"blocks": [...], "document_revision_id": int}`

### delete_blocks(document_id, block_id, start_index, end_index)

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| document_id | str | **Yes** | Document ID | — |
| block_id | str | **Yes** | Parent block ID | — |
| start_index | int | **Yes** | Start (inclusive) | >= 0 |
| end_index | int | **Yes** | End (exclusive) | >= 1 |

Deletes children at positions `[start_index, end_index)`.

**Returns**: `{"document_revision_id": int, "client_token": str}`

---

## Convenience Helpers

### create_text_block(document_id, parent_block_id, text, bold, italic)

Wraps `create_blocks` with single text block (block_type=2).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Text content |
| bold | bool | No | Bold (default False) |
| italic | bool | No | Italic (default False) |

### create_heading_block(document_id, parent_block_id, text, level)

Wraps `create_blocks` with heading block. Level 1-9 maps to block_type 3-11.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Heading text |
| level | int | No | 1-9 (default 1) |

### create_todo_block(document_id, parent_block_id, text, done)

Wraps `create_blocks` with todo block (block_type=17).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | **Yes** | Todo text |
| done | bool | No | Completed (default False) |

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Write (create/update/delete blocks) | 3/sec per document |
| Read (get/list) | 5/sec per app |
| App-level calls | 3/sec per endpoint |

**Retry**: Exponential backoff (2s, 4s, 8s) built into `LarkAPIBase`.

---

## Error Codes

| Code | HTTP | Message | Fix |
|------|------|---------|-----|
| 0 | 200 | Success | Continue |
| 1770001 | 400 | Invalid param | Check request body fields |
| 1770002 | 404 | Not found | Document may be deleted |
| 1770003 | 400 | Resource deleted | Resource no longer exists |
| 1770004 | 400 | Too many blocks | Max blocks per document exceeded |
| 1770007 | 400 | Too many children | Max children per block exceeded |
| 1770014 | 400 | Parent-child mismatch | Invalid block nesting |
| 1770028 | 400 | Block can't have children | Block type doesn't support children |
| 1770032 | 403 | Forbidden | Check document permissions |
| 1770039 | 404 | Folder not found | Check folder_token |
| 1770040 | 403 | No folder permission | No create permission in folder |
| 1771001 | 500 | Server error | Retry |
| 99991663 | 401 | Token expired | MCP `refresh_lark_token` |
| 99991664 | 403 | Permission denied | Check app scopes |
| 1254290 | 429 | Rate limited | Backoff (2s, 4s, 8s) |
