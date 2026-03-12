# Lark Docs API Examples

> All examples assume the client is initialized per [SKILL.md](../SKILL.md).
> See [api-reference.md](./api-reference.md) for param details.
> See [api-validation.md](./api-validation.md) for block types and error codes.

---

## 1. Create Document and Add Content

```python
# Create document
result = client.create_document(title="Meeting Notes")
doc_id = result["document"]["document_id"]

# Page block_id == document_id (root of block tree)
import time
time.sleep(1)  # rate limit: 3 writes/sec per doc

# Add heading
client.create_heading_block(doc_id, doc_id, "Action Items", level=1)
time.sleep(1)

# Add text
client.create_text_block(doc_id, doc_id, "Review Q3 targets", bold=True)
time.sleep(1)

# Add todo items
client.create_todo_block(doc_id, doc_id, "Update roadmap", done=False)
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Send follow-up email", done=True)
```

---

## 2. Read Document Content

```python
# Plain text content
raw = client.get_raw_content(doc_id)
print(raw.get("content", ""))

# Structured blocks
blocks = client.list_blocks(doc_id)
for b in blocks:
    btype = b.get("block_type")
    bid = b.get("block_id")
    print(f"  [{btype}] {bid}")
```

---

## 3. Create Complex Block Structure

```python
# Create multiple blocks in one call (1-50 per call)
blocks = [
    {
        "block_type": 3,  # heading1
        "heading1": {
            "elements": [{"text_run": {"content": "Section Title"}}]
        }
    },
    {
        "block_type": 2,  # text
        "text": {
            "elements": [
                {"text_run": {"content": "Normal text "}},
                {"text_run": {"content": "bold text", "text_element_style": {"bold": True}}},
            ]
        }
    },
    {
        "block_type": 12,  # bullet list
        "bullet": {
            "elements": [{"text_run": {"content": "First bullet point"}}]
        }
    },
]
result = client.create_blocks(doc_id, doc_id, blocks)
created = result.get("children", [])
print(f"Created {len(created)} blocks")
```

---

## 4. Update Block Text

```python
block_id = created[0]["block_id"]  # from previous create

client.update_block(doc_id, block_id, update_text_elements={
    "elements": [
        {"text_run": {"content": "Updated Section Title", "text_element_style": {"bold": True}}}
    ]
})
```

---

## 5. Batch Update Multiple Blocks

```python
requests = [
    {
        "block_id": block_id_1,
        "update_text_elements": {
            "elements": [{"text_run": {"content": "Updated text 1"}}]
        }
    },
    {
        "block_id": block_id_2,
        "update_text_elements": {
            "elements": [{"text_run": {"content": "Updated text 2"}}]
        }
    },
]
client.batch_update_blocks(doc_id, requests)  # max 200 per call
```

---

## 6. Delete Blocks by Index Range

```python
# Get children to see current order
children = client.get_block_children(doc_id, doc_id)
print(f"Before: {len(children)} children")

# Delete first 2 children [0, 2)
client.delete_blocks(doc_id, doc_id, start_index=0, end_index=2)

children = client.get_block_children(doc_id, doc_id)
print(f"After: {len(children)} children")
```

---

## 7. Full Workflow: Create, Populate, Read Back

```python
import time

# 1. Create
result = client.create_document(title="Sprint Planning")
doc_id = result["document"]["document_id"]
time.sleep(1)

# 2. Add heading + items
client.create_heading_block(doc_id, doc_id, "Sprint Goals", level=1)
time.sleep(1)
client.create_text_block(doc_id, doc_id, "Deliver auth module by Friday")
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Design API schema")
time.sleep(1)
client.create_todo_block(doc_id, doc_id, "Write unit tests")
time.sleep(1)

# 3. Read back
raw = client.get_raw_content(doc_id)
print(raw.get("content", ""))

# 4. List blocks for structure
blocks = client.list_blocks(doc_id)
for b in blocks:
    indent = "  " if b.get("parent_id") == doc_id else "    "
    print(f"{indent}[{b['block_type']}] {b['block_id']}")
```
