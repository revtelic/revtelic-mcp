"""
CrewAI Tool Adapter for Revtelic.
"""
from __future__ import annotations

from typing import Any, Optional, Type
from pydantic import BaseModel, Field

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
except ImportError:
    try:
        from crewai_tools import BaseTool as CrewAIBaseTool
    except ImportError:
        CrewAIBaseTool = object  # type: ignore

from ..client import RevtelicClient


class AnalyzeDealInput(BaseModel):
    transcript: str = Field(..., description="Sales call transcript, email thread, or meeting notes")
    name: Optional[str] = Field(None, description="Optional opportunity name")


class RevtelicDealAnalyzerTool(CrewAIBaseTool):  # type: ignore
    """CrewAI tool for analyzing sales deal conversations with Revtelic."""

    name: str = "Revtelic Deal Health Analyzer"
    description: str = (
        "Analyzes raw sales meeting transcripts or notes. Returns 0-100 deal health score, "
        "brutal truth, risks, buyer champions, next best action, and one-pager link."
    )
    args_schema: Type[BaseModel] = AnalyzeDealInput

    def _run(self, transcript: str, name: Optional[str] = None) -> str:
        client = RevtelicClient()
        analysis = client.analyze(transcript=transcript, name=name)
        return (
            f"Health Score: {analysis.health_score}/100\n"
            f"Brutal Truth: {analysis.brutal_truth}\n"
            f"Key Risks: {analysis.risks}\n"
            f"Next Action: {analysis.next_best_action}\n"
            f"One-Pager Link: {analysis.one_pager_url}"
        )
