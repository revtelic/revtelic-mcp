# Revtelic Python SDK & MCP Server

Official Python client and Model Context Protocol (MCP) server for [Revtelic](https://revtelic.com).

Evaluate B2B sales call transcripts and notes with zero-friction Deal Health Intelligence directly in Python, **LangChain**, **CrewAI**, or as an MCP server for **Claude Desktop** and **Cursor**.

---

## 📦 Installation

```bash
pip install revtelic

# With LangChain support:
pip install "revtelic[langchain]"

# With CrewAI support:
pip install "revtelic[crewai]"
```

---

## ⚡ 1. Zero-Friction Python Usage (No API Key Required)

```python
from revtelic import RevtelicClient

# Unauthenticated / guest mode works out of the box!
client = RevtelicClient()

analysis = client.analyze(
    transcript="""
    Dave (VP Sales): We love what you showed today. 
    Sarah (Security): We need an automated SOC2 review and legal won't sign before Q4.
    Dave: Let's reconnect in 3 weeks.
    """,
    name="Stripe - Security Module Expansion"
)

print(f"Deal Health: {analysis.health_score}/100")
print(f"Brutal Truth: {analysis.brutal_truth}")
print(f"Key Risks: {analysis.risks}")
print(f"Interactive One-Pager: {analysis.one_pager_url}")
```

### Async Analysis:
```python
import asyncio
from revtelic import RevtelicClient

async def main():
    client = RevtelicClient()
    analysis = await client.analyze_async(transcript="...")
    print(analysis.health_score)

asyncio.run(main())
```

---

## 🤖 2. LangChain Integration

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from revtelic.adapters.langchain import RevtelicAnalyzeTool

llm = ChatOpenAI(model="gpt-4o")
tools = [RevtelicAnalyzeTool()]

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

response = executor.invoke({
    "input": "Analyze this call transcript: Dave agreed to a trial but has no budget..."
})
```

---

## 🚀 3. Run as an MCP Server (`uvx` or `python -m`)

You can run Revtelic directly as a stdio MCP server for Claude Desktop or Cursor:

### Using `uvx` (Zero-install):
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

### With optional API Key (saves deals to your Revtelic workspace):
```json
{
  "mcpServers": {
    "revtelic": {
      "command": "uvx",
      "args": ["revtelic-mcp"],
      "env": {
        "REVTELIC_API_KEY": "rev_live_YOUR_KEY"
      }
    }
  }
}
```

---

## 📄 License
Apache-2.0
