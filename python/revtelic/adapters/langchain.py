"""
LangChain Tool Adapter for Revtelic.
"""
from __future__ import annotations

from typing import Any, Optional, Type
from pydantic import BaseModel, Field

try:
    from langchain_core.tools import BaseTool
except ImportError:
    BaseTool = object  # type: ignore

from ..client import RevtelicClient


class AnalyzeDealInput(BaseModel):
    transcript: str = Field(..., description="Raw sales call transcript, email thread, or meeting notes")
    name: Optional[str] = Field(None, description="Optional opportunity or company name")


class RevtelicAnalyzeTool(BaseTool):  # type: ignore
    """Tool that analyzes sales call transcripts using Revtelic Deal Intelligence."""

    name: str = "revtelic_analyze_deal"
    description: str = (
        "Useful for analyzing B2B sales call transcripts, email threads, or meeting notes. "
        "Returns health score (0-100), brutal truth, top risks, stakeholders, next best action, and one-pager link."
    )
    args_schema: Type[BaseModel] = AnalyzeDealInput
    client: Optional[RevtelicClient] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = RevtelicClient(api_key=api_key)

    def _run(self, transcript: str, name: Optional[str] = None) -> str:
        client = self.client or RevtelicClient()
        analysis = client.analyze(transcript=transcript, name=name)
        return (
            f"Health Score: {analysis.health_score}/100\n"
            f"Brutal Truth: {analysis.brutal_truth}\n"
            f"Risks: {analysis.risks}\n"
            f"Next Action: {analysis.next_best_action}\n"
            f"One Pager URL: {analysis.one_pager_url}"
        )

    async def _arun(self, transcript: str, name: Optional[str] = None) -> str:
        client = self.client or RevtelicClient()
        analysis = await client.analyze_async(transcript=transcript, name=name)
        return (
            f"Health Score: {analysis.health_score}/100\n"
            f"Brutal Truth: {analysis.brutal_truth}\n"
            f"Risks: {analysis.risks}\n"
            f"Next Action: {analysis.next_best_action}\n"
            f"One Pager URL: {analysis.one_pager_url}"
        )
