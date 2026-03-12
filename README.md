# Lark Skills

Production-grade AI agent skills for LarkSuite enterprise workspace. Manage calendars, tasks, docs, and more through Claude Code or any compatible AI agent.

## Available Skills

| Skill | Description | Methods | Status |
|-------|-------------|---------|--------|
| lark-calendar | Events, attendees, scheduling | 5 | Production |
| lark-task | Tasks, subtasks, tasklists, sections, custom fields | 24 | Production |
| lark-token-manager | OAuth token lifecycle (shared MCP server) | 16 | Production |
| lark-messenger | Messages, cards, group chats, file sharing | 16 | Production |
| lark-contacts | People, departments, user groups | 10 | Production |
| lark-base | Bitable databases, records, forms | 36 | Production |
| lark-base-formula | Formula reference, 100+ functions, cross-table patterns | 0 | Production |
| lark-docs | Document creation, block editing | 13 | Production |
| lark-drive | File upload, download, search, folder management, permissions | 15 | Production |
| lark-sheets | Spreadsheet read/write, formatting | 17 | Production |
| lark-wiki | Wiki spaces, node tree, members, search | 15 | Production |

## Quickstart

```bash
# 1. Install plugin marketplace
/plugin marketplace add kesflow/lark-skills

# 2. Install token manager (required by all skills)
/plugin install lark-token-manager@lark-skills

# 3. Install desired skills
/plugin install lark-calendar@lark-skills
/plugin install lark-task@lark-skills

# 4. Configure MCP connection
cp .mcp.json.example .mcp.json  # Edit: add MCP URL + API key (hardcoded, gitignored)

# 5. Test
# Ask: "What's on my calendar today?"
```

## Architecture

```
AI Agent (Claude Code / Antigravity)
    │
    ├─ lark-calendar agent ──┐
    ├─ lark-task agent ──────┤
    ├─ lark-messenger agent ─┤──── Lark Open APIs
    └─ ...                   │    (open.larksuite.com)
                              │
    lark-token-manager MCP ───┘
    (Supabase Edge Functions)
        │
        └── OAuth tokens (Vault-encrypted)
```

Each plugin: `agents/` (dedicated subagent) + `SKILL.md` (agent guide) + `scripts/` (Python API client) + `references/` (3-layer API docs) + `.mcp.json` (auto-config).

## Pricing

$10-15/skill/org/month flat rate. No API fees — you use your own Lark app and AI agent.

## Documentation

- [Getting Started](docs/setup-guide.md) — Enterprise setup guide
- [System Architecture](docs/system-architecture.md) — Technical design
- [Code Standards](docs/code-standards.md) — Development conventions
- [Lark Skill Creator](.claude/skills/lark-skill-creator/SKILL.md) — Primary tool to scaffold & validate new plugins (automated, 7-step)
- [Building Skills (Legacy)](plugins/lark-token-manager/skills/lark-token-manager/references/lark-skill-builder-guide.md) — Deprecated manual guide, superseded by lark-skill-creator
- [Full docs index](docs/README.md)

## License

Proprietary. All rights reserved.
