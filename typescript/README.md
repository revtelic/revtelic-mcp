# @revtelic/mcp

Official Model Context Protocol (MCP) server and TypeScript SDK for [Revtelic](https://revtelic.com).

Evaluate B2B sales call transcripts and notes with zero-friction Deal Health Intelligence directly inside **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity**.

---

## ⚡ Quickstart

### Option 1: Run instantly with `npx` (No Install Needed)

Add to your **Claude Desktop** config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "revtelic": {
      "command": "npx",
      "args": ["-y", "@revtelic/mcp"]
    }
  }
}
```

Or add to **Cursor** (`~/.cursor/mcp.json` or `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "revtelic": {
      "command": "npx",
      "args": ["-y", "@revtelic/mcp"],
      "env": {
        "REVTELIC_API_KEY": "rev_live_YOUR_KEY" 
      }
    }
  }
}
```
*(Note: `REVTELIC_API_KEY` is optional! Omit it for open, zero-friction guest mode).*

---

## 🛠️ Tools Provided

| Tool | Auth Required | Description |
|---|---|---|
| `analyze_deal` | ❌ No (Guest Mode) | Takes a raw meeting transcript or call notes and returns health score (0-100), brutal truth, top risks, stakeholders, next best action, and an interactive One-Pager link. |
| `get_deal_health` | ✅ Yes | Returns health score, momentum signals, and slip risk for a saved deal. |
| `get_deal_risks` | ✅ Yes | Analyzes hidden blockers, commercial, and technical risks. |
| `get_stakeholders` | ✅ Yes | Maps buyer champions, economic buyer access, and missing contacts. |
| `get_next_best_action` | ✅ Yes | Determines the single highest-leverage next move to close the deal. |
| `list_deals` | ✅ Yes | Lists dealboards in your workspace. |

---

## 💻 Programmatic TypeScript SDK Usage

You can also use this package as a standard Node/TypeScript library:

```typescript
import { RevtelicClient } from "@revtelic/mcp";

// 1. Zero friction guest mode
const client = new RevtelicClient();
const result = await client.analyzeDeal({
  transcript: "Dave: We love the demo, but legal review takes 6 weeks...",
  name: "Acme Corp Expansion"
});

console.log(`Health: ${result.health_score}/100`);
console.log(`Brutal Truth: ${result.brutal_truth}`);
console.log(`View One-Pager: ${result.one_pager_url}`);

// 2. Authenticated mode (saved to workspace)
const authClient = new RevtelicClient({ apiKey: "rev_live_..." });
const deals = await authClient.listDeals();
```

---

## 📄 License
Apache-2.0
