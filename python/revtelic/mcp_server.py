"""
Revtelic FastMCP Server Runner.
Provides stdio transport for Claude Desktop, Cursor, Windsurf, and Antigravity.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # type: ignore

from .client import RevtelicClient


def create_server() -> Any:
    if FastMCP is None:
        raise RuntimeError("The 'mcp' package is required: pip install mcp")

    mcp = FastMCP("revtelic-mcp")
    client = RevtelicClient()

    @mcp.tool()
    def analyze_deal(
        transcript: str,
        name: Optional[str] = None,
    ) -> str:
        """Analyse a raw B2B sales call transcript, meeting notes, sales conversation, or email thread and produce a Revtelic Deal Health Intelligence assessment. Returns 0-100 deal health, buyer commitment, brutal truth, strengths, risks, stakeholder intelligence, qualification gaps, next best action, and an interactive Deal Health One-Pager URL. Open for zero-friction deal analysis without requiring an account or API key."""
        analysis = client.analyze(transcript=transcript, name=name)

        score = analysis.health_score
        status = "Healthy" if score >= 70 else "At Risk / Slipping" if score >= 50 else "Critical / Stalled"

        md = [
            f"# 🎯 Revtelic Deal Health Intelligence: {analysis.name or 'Sales Opportunity'}",
            f"**Deal Health Score**: **{score}/100** ({status})\n",
            f"### 💥 Brutal Truth\n{analysis.brutal_truth}\n",
        ]

        if analysis.risks:
            md.append("### ⚠️ Key Deal Risks")
            for r in analysis.risks:
                if isinstance(r, dict):
                    md.append(f"- **{r.get('type', 'Risk')}**: {r.get('description', '')}")
                else:
                    md.append(f"- {r}")
            md.append("")

        if analysis.stakeholders:
            md.append("### 👥 Stakeholder Map")
            for s in analysis.stakeholders:
                if isinstance(s, dict):
                    role = f" ({s.get('role')})" if s.get("role") else ""
                    md.append(f"- **{s.get('name')}**{role}: sentiment={s.get('sentiment')}")
                else:
                    md.append(f"- {s}")
            md.append("")

        if analysis.next_best_action:
            md.append("### 🚀 Next Best Action")
            if isinstance(analysis.next_best_action, dict):
                md.append(f"**Action**: {analysis.next_best_action.get('action')}")
                if analysis.next_best_action.get("rationale"):
                    md.append(f"*Rationale*: {analysis.next_best_action.get('rationale')}")
            else:
                md.append(f"{analysis.next_best_action}")
            md.append("")

        if analysis.one_pager_url:
            md.append("---")
            md.append(f"📊 **Interactive Deal One-Pager**: [Open Dealboard in Revtelic]({analysis.one_pager_url})")

        return "\n".join(md) + f"\n\n```json\n{json.dumps(analysis.model_dump(), indent=2, default=str)}\n```"

    @mcp.tool()
    def get_deal_health(deal_id: str) -> str:
        """Assess the health of a saved B2B sales opportunity in Revtelic and return a 0–100 health score with the reasons behind it. Requires Revtelic account or REVTELIC_API_KEY."""
        result = client.get_deal_health(deal_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    def get_deal_risks(deal_id: str) -> str:
        """Identify critical hidden blockers and explicit risks that could prevent a saved sales deal from closing. Requires Revtelic account or REVTELIC_API_KEY."""
        result = client.get_deal_risks(deal_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    def get_stakeholders(deal_id: str) -> str:
        """Analyse the stakeholder landscape of a saved deal, including champion strength, economic buyer access, and missing stakeholders. Requires Revtelic account or REVTELIC_API_KEY."""
        result = client.get_stakeholders(deal_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    def get_next_best_action(deal_id: str) -> str:
        """Determine the single highest-priority action the seller should take next to progress or close a saved deal. Requires Revtelic account or REVTELIC_API_KEY."""
        result = client.get_next_best_action(deal_id)
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    def list_deals(search: Optional[str] = None, limit: int = 20) -> str:
        """List active dealboards from your connected Revtelic workspace. Requires Revtelic account or REVTELIC_API_KEY."""
        result = client.list_deals(search=search, limit=limit)
        return json.dumps(result, indent=2, default=str)

    return mcp


def main() -> None:
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
