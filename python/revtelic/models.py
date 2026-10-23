"""
Revtelic Data Models for Deal Health Intelligence.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DealRisk(BaseModel):
    type: str = Field(..., description="Category of risk (commercial, timing, stakeholder, etc.)")
    severity: str = Field("medium", description="Risk severity: critical, high, medium, low")
    description: str = Field(..., description="Unvarnished diagnosis of the risk")
    evidence: Optional[str] = Field(None, description="Direct quote or signal from conversation")
    mitigation: Optional[str] = Field(None, description="Recommended seller action to de-risk")


class Stakeholder(BaseModel):
    name: str = Field(..., description="Stakeholder name or inferred persona")
    role: Optional[str] = Field(None, description="Job title or functional role")
    sentiment: Optional[str] = Field("unknown", description="champion, supporter, neutral, blocker, unknown")
    influence: Optional[str] = Field("medium", description="high, medium, low")
    is_economic_buyer: Optional[bool] = Field(False, description="Whether stakeholder holds budget authority")


class NextAction(BaseModel):
    action: str = Field(..., description="Specific recommendation for the next step")
    rationale: Optional[str] = Field(None, description="Strategic rationale for why this action matters")
    owner: Optional[str] = Field(None, description="Person responsible for executing action")
    deadline: Optional[str] = Field(None, description="Target timeframe or milestone")


class DealAnalysis(BaseModel):
    deal_id: Optional[str] = Field(None, description="Persistent or temporary deal ID")
    name: Optional[str] = Field(None, description="Deal or opportunity name")
    health_score: int = Field(50, description="Overall Deal Health Score (0-100)")
    status: Optional[str] = Field("healthy", description="healthy, slipping, critical, stalled")
    brutal_truth: str = Field("", description="Unvarnished, objective deal diagnosis")
    strengths: List[str] = Field(default_factory=list, description="Positive deal signals")
    risks: List[Any] = Field(default_factory=list, description="Uncovered deal killers and blockers")
    stakeholders: List[Any] = Field(default_factory=list, description="Stakeholder intelligence")
    qualification_gaps: List[str] = Field(default_factory=list, description="Missing MEDDICC/BANT criteria")
    next_best_action: Optional[Any] = Field(None, description="Top priority next move")
    one_pager_url: Optional[str] = Field(None, description="Interactive web Deal Health One-Pager URL")
    claim_and_save_url: Optional[str] = Field(None, description="URL to claim and save deal to workspace")
    raw: Dict[str, Any] = Field(default_factory=dict, description="Raw API response data")

    @property
    def is_healthy(self) -> bool:
        return self.health_score >= 70

    @property
    def is_critical(self) -> bool:
        return self.health_score < 50
