# Lark Docs Validation Reference

> See [api-reference.md](./api-reference.md) for method signatures.
> See [api-examples.md](./api-examples.md) for code samples.

---

## Block Type Enum

| ID | Type | Key in block object | Can have children |
|----|------|---------------------|-------------------|
| 1 | Page | `page` | Yes (root block) |
| 2 | Text | `text` | No |
| 3-11 | Heading 1-9 | `heading1`-`heading9` | No |
| 12 | Bullet List | `bullet` | No |
| 13 | Ordered List | `ordered` | No |
| 14 | Code Block | `code` | No |
| 15 | Quote | `quote` | No |
| 17 | Todo | `todo` | No |
| 18 | Bitable | `bitable` | No |
| 19 | Callout | `callout` | Yes |
| 22 | Divider | `divider` | No |
| 23 | File | `file` | No |
| 24 | Grid | `grid` | Yes (grid columns) |
| 25 | Grid Column | `grid_column` | Yes |
| 27 | Image | `image` | No |
| 31 | Table | `table` | Yes (table cells) |
| 32 | Table Cell | `table_cell` | Yes |
| 34 | Quote Container | `quote_container` | Yes |

---

## Parent-Child Rules

| Parent Type | Allowed Children |
|-------------|-----------------|
| Page (1) | Text, Heading, Bullet, Ordered, Code, Quote, Todo, Callout, Divider, Grid, Table, Image, File, Bitable, Quote Container |
| Callout (19) | Text, Heading, Bullet, Ordered, Code, Quote, Todo, Divider, Image |
| Grid (24) | Grid Column only |
| Grid Column (25) | Same as Page (except Grid) |
| Table (31) | Table Cell only |
| Table Cell (32) | Text, Heading, Bullet, Ordered, Todo |
| Quote Container (34) | Text, Heading, Bullet, Ordered, Code, Todo |

---

## Text Element Types

```
text_element
├── text_run        # Plain text with optional style
│   ├── content     # string (required)
│   └── text_element_style
│       ├── bold, italic, strikethrough, underline, inline_code  # bool
│       ├── background_color  # int 1-15
│       ├── text_color        # int 1-7
│       └── link              # {url: string} (url-encoded)
├── mention_user    # @user
│   └── user_id     # OpenID string
├── mention_doc     # @document
│   ├── token       # document token
│   ├── obj_type    # 1=doc, 3=sheet, 8=bitable, 12=slides, 15=mindnote, 16=docx, 22=wiki
│   └── url         # document URL
├── equation        # LaTeX equation
│   └── content     # LaTeX string
└── reminder        # Date reminder
    ├── create_user_id  # creator OpenID
    ├── expire_time     # MILLISECONDS (13-digit timestamp)
    └── notify_time     # MILLISECONDS (13-digit timestamp)
```

---

## TextStyle (block-level style)

```
style
├── align       # 1=left, 2=center, 3=right
├── done        # bool (todo blocks only)
├── folded      # bool (collapsible blocks)
├── language    # int 1-75 (code blocks only, see language enum)
└── wrap        # bool (code block auto-wrap)
```

---

## Field Constraints

| Field | Constraint |
|-------|-----------|
| title | 1-800 characters |
| children (create_blocks) | 1-50 blocks per call |
| requests (batch_update) | Max 200 per call |
| page_size (list/get_children) | Max 500 |
| heading level | 1-9 (maps to block_type 3-11) |
| delete index range | [start_index, end_index) — left-closed, right-open |
| document_id | 27 characters |
| link url | Must be URL-encoded |
| Reminder timestamps | MILLISECONDS (13 digits) |

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Write ops (create/update/delete blocks) | 3/sec per document |
| Read ops (get/list) | 5/sec per app |
| App-level API calls | 3/sec per endpoint |

**Retry**: Exponential backoff (2s, 4s, 8s) built into `LarkAPIBase` for code 1254290.

---

## Error Code Reference

| Code | HTTP | Message | Fix |
|------|------|---------|-----|
| 0 | 200 | Success | — |
| 1770001 | 400 | Invalid param | Check field names/types/required |
| 1770002 | 404 | Not found | Document deleted or wrong ID |
| 1770003 | 400 | Resource deleted | Resource no longer exists |
| 1770004 | 400 | Too many blocks | Document block limit exceeded |
| 1770005 | 400 | Too deep level | Block nesting depth exceeded |
| 1770006 | 400 | Schema mismatch | Invalid document structure |
| 1770007 | 400 | Too many children | Max children per block exceeded |
| 1770010 | 400 | Too many table columns | Table column limit exceeded |
| 1770011 | 400 | Too many table cells | Table cell limit exceeded |
| 1770012 | 400 | Too many grid columns | Grid column limit exceeded |
| 1770014 | 400 | Parent-child mismatch | Invalid block nesting relationship |
| 1770022 | 400 | Invalid page_token | Bad pagination token |
| 1770024 | 400 | Invalid operation | Check operation type |
| 1770025 | 400 | Op/block mismatch | Wrong operation for block type |
| 1770028 | 400 | No children allowed | Block type can't have children |
| 1770029 | 400 | Block can't be created | Block type not supported for creation |
| 1770031 | 400 | Can't delete children | Block type doesn't support child deletion |
| 1770032 | 403 | Forbidden | Check document permissions |
| 1770036 | 400 | Folder locked | Serialize document creation in same folder |
| 1770039 | 404 | Folder not found | Check folder_token |
| 1770040 | 403 | No folder permission | No create permission in folder |
| 1771001 | 500 | Server error | Retry |
| 1771005 | 503 | Under maintenance | Wait and retry |
| 99991663 | 401 | Token expired | MCP `refresh_lark_token` |
| 99991664 | 403 | Permission denied | Check app scopes |
| 1254290 | 429 | Rate limited | Backoff (2s, 4s, 8s) |
