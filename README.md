# Revtelic MCP Client SDK & Server 🎯

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue?style=flat-square&logo=anthropic)](https://modelcontextprotocol.io)
[![npm version](https://img.shields.io/npm/v/@revtelic/mcp.svg?style=flat-square)](https://www.npmjs.com/package/@revtelic/mcp)
[![PyPI version](https://img.shields.io/pypi/v/revtelic.svg?style=flat-square)](https://pypi.org/project/revtelic/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg?style=flat-square)](https://opensource.org/licenses/Apache-2.0)

**Instant, zero-friction B2B sales deal intelligence for AI assistants and autonomous agents.**

Connect [Revtelic](https://revtelic.com) to **Claude Desktop**, **Cursor**, **Windsurf**, **ChatGPT**, **LangChain**, and **CrewAI** to automatically analyze meeting transcripts, call notes, and sales emails into:

- 🎯 **Deal Health Score (0–100)** with real-time momentum diagnosis
- 💥 **The Brutal Truth** — unvarnished assessment of whether the deal is real
- ⚠️ **Hidden Deal Killers** (commercial, technical, timing, and procurement risks)
- 👥 **Stakeholder Intelligence** (champion strength, economic buyer access, missing blockers)
- 🚀 **Next Best Action** to unblock and close the opportunity
- 📊 **Interactive Deal One-Pager link** to collaborate with buyers or claim into your Revtelic workspace

---

## ⚡ Zero-Friction Quickstart (No API Key Required)

Revtelic MCP works in **guest mode out-of-the-box**. Anyone can paste a sales transcript into their AI assistant and get deal health intelligence immediately without signing up.

### 1. Claude Desktop

Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

#### Using `npx` (TypeScript / Node):
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

#### Or using `uvx` (Python):
```json
{
  "mcpServers": {
    "revtelic": {
      "command": "uvx",
      "args": ["revtelic-mcp"]
    }
  }
}
```

---

### 2. Cursor IDE

In Cursor, open **Cursor Settings → MCP**, or edit `~/.cursor/mcp.json` / `.cursor/mcp.json`:

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

---

### 3. Direct Remote Streamable HTTP (Claude Web / ChatGPT / Inspector)

If your client supports remote HTTP MCP servers directly without a local subprocess:

- **Server URL**: `https://api.revtelic.com/api/v1/mcp`
- **SSE Fallback**: `https://api.revtelic.com/api/v1/mcp/sse`
- **Auth**: None required for `analyze_deal` (Guest Mode).

---

## 🔑 Workspace Sync Mode (Optional)

If you have a [Revtelic](https://app.revtelic.com) account, you can pass your API key to automatically save analyses to your workspace dealboards:

```json
{
  "mcpServers": {
    "revtelic": {
      "command": "npx",
      "args": ["-y", "@revtelic/mcp"],
      "env": {
        "REVTELIC_API_KEY": "rev_live_YOUR_API_KEY"
      }
    }
  }
}
```

---

## 🛠️ MCP Tools Overview

| Tool | Requires Auth? | Description |
|---|---|---|
| `analyze_deal` | ❌ **No (Guest Mode)** | Evaluates raw sales transcript/notes. Returns deal health, brutal truth, risks, stakeholders, next best action, and web one-pager link. |
| `get_deal_health` | ✅ Yes | Returns 0–100 health score, momentum signals, and slip risk for a saved deal. |
| `get_deal_risks` | ✅ Yes | Identifies hidden blockers and explicit commercial/technical deal risks. |
| `get_stakeholders` | ✅ Yes | Maps buyer champions, economic buyer access, and missing contacts. |
| `get_next_best_action` | ✅ Yes | Determines the single highest-priority move to progress or close the deal. |
| `list_deals` | ✅ Yes | Lists active dealboards from the connected Revtelic workspace. |

---

## 🐍 Python SDK & AI Agent Workflows

### 1. Programmatic Python Client

```bash
pip install revtelic
```

```python
from revtelic import RevtelicClient

# Frictionless guest mode
client = RevtelicClient()

analysis = client.analyze(
    transcript="""
    Rep: How does our pricing look for the enterprise tier?
    Prospect: We love the features, but procurement has frozen all new vendor spend until Q4.
    Rep: Can we do a pilot?
    Prospect: Only if it's free and Dave from IT approves it.
    """,
    name="Stripe Pilot Deal"
)

print(f"Health Score: {analysis.health_score}/100")
print(f"Brutal Truth: {analysis.brutal_truth}")
print(f"One-Pager URL: {analysis.one_pager_url}")
```

### 2. LangChain Integration

```bash
pip install "revtelic[langchain]"
```

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from revtelic.adapters.langchain import RevtelicAnalyzeTool

llm = ChatOpenAI(model="gpt-4o")
tools = [RevtelicAnalyzeTool()]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({
    "input": "Review our call with Acme Corp and identify any hidden risks: [TRANSCRIPT]"
})
```

### 3. CrewAI Integration

```bash
pip install "revtelic[crewai]"
```

```python
from crewai import Agent
from revtelic.adapters.crewai import RevtelicDealAnalyzerTool

deal_evaluator = Agent(
    role="B2B Deal Strategist",
    goal="Diagnose deal health and identify deal blockers",
    backstory="You are an expert enterprise sales director inspecting pipeline accuracy.",
    tools=[RevtelicDealAnalyzerTool()]
)
```

---

## 🌐 TypeScript SDK Usage

```bash
npm install @revtelic/mcp
```

```typescript
import { RevtelicClient } from "@revtelic/mcp";

const client = new RevtelicClient();
const result = await client.analyzeDeal({
  transcript: "Dave: We love the product but legal review takes 6 weeks...",
  name: "Acme Renewal"
});

console.log(result.health_score, result.brutal_truth);
```

---

## 📦 Directory Structure

```
revtelic-mcp/
├── server.json             # Official MCP Registry & Smithery manifest
├── README.md               # Main documentation
├── LICENSE                 # Apache 2.0
├── typescript/             # TypeScript MCP stdio server (@revtelic/mcp)
│   ├── package.json
│   ├── src/
│   │   ├── index.ts        # Stdio MCP server runner
│   │   ├── client.ts       # HTTP Client
│   │   └── types.ts
│   └── bin/revtelic-mcp.js # CLI entrypoint
└── python/                 # Python SDK & FastMCP server (revtelic)
    ├── pyproject.toml
    ├── revtelic/
    │   ├── client.py       # Core Python SDK
    │   ├── mcp_server.py   # FastMCP stdio server
    │   ├── models.py       # Pydantic models
    │   └── adapters/       # LangChain & CrewAI tools
    └── README.md
```

---

## 🤝 Contributing & Submitting to MCP Registries

This server conforms to the official [Model Context Protocol schema](https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json).

To submit to the official Model Context Protocol server list:
1. Fork [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).
2. Point to this repo and `server.json`.
3. Submit a PR.

---

## 📄 License

Distributed under the Apache-2.0 License. See `LICENSE` for details.
