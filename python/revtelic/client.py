"""
Revtelic Python Client SDK.
Zero-friction deal analysis & workspace sync.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Union

import httpx

from .models import DealAnalysis, DealRisk, NextAction, Stakeholder

DEFAULT_API_BASE = "https://api.revtelic.com"


class RevtelicClient:
    """
    Official Python Client for Revtelic.

    Usage:
        # Zero-friction guest mode (no API key needed)
        client = RevtelicClient()
        analysis = client.analyze("Dave: We love the demo but need procurement signoff...")
        print(analysis.health_score, analysis.brutal_truth)

        # Authenticated workspace mode
        client = RevtelicClient(api_key="rev_live_...")
        deals = client.list_deals()
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_base = (
            api_base
            or os.getenv("REVTELIC_API_BASE_URL")
            or os.getenv("DEALWIZE_API_BASE_URL")
            or DEFAULT_API_BASE
        ).rstrip("/")

        self.api_key = (
            api_key
            or os.getenv("REVTELIC_API_KEY")
            or os.getenv("DEALWIZE_API_KEY")
        )
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "revtelic-python-sdk/1.0.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    # -------------------------------------------------------------------------
    # Core Analysis (Synchronous)
    # -------------------------------------------------------------------------

    def analyze(
        self,
        transcript: str,
        name: Optional[str] = None,
    ) -> DealAnalysis:
        """
        Analyze a raw meeting transcript, notes, or email thread.
        Works in zero-friction guest mode without requiring an account.
        """
        transcript_clean = (transcript or "").strip()
        if not transcript_clean:
            raise ValueError("transcript cannot be empty")

        url = f"{self.api_base}/api/v1/mcp"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "analyze_deal",
                "arguments": {
                    "transcript": transcript_clean,
                    "name": name,
                },
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    url,
                    headers={**self._headers(), "Accept": "application/json, text/event-stream"},
                    json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("result", {}).get("content", [])
                    if content and isinstance(content, list) and content[0].get("text"):
                        raw_text = content[0]["text"]
                        try:
                            parsed = json.loads(raw_text)
                            return DealAnalysis(**parsed, raw=parsed)
                        except Exception:
                            pass
        except Exception:
            pass

        # Fallback to public analyse REST endpoint
        fallback_url = f"{self.api_base}/api/v1/public/analyse"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                fallback_url,
                headers=self._headers(),
                json={"transcript": transcript_clean, "name": name},
            )
            resp.raise_for_status()
            res_json = resp.json()
            data = res_json.get("data") or res_json
            return DealAnalysis(**data, raw=data)

    # -------------------------------------------------------------------------
    # Core Analysis (Asynchronous)
    # -------------------------------------------------------------------------

    async def analyze_async(
        self,
        transcript: str,
        name: Optional[str] = None,
    ) -> DealAnalysis:
        """
        Asynchronously analyze a sales meeting transcript or notes.
        """
        transcript_clean = (transcript or "").strip()
        if not transcript_clean:
            raise ValueError("transcript cannot be empty")

        url = f"{self.api_base}/api/v1/mcp"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "analyze_deal",
                "arguments": {
                    "transcript": transcript_clean,
                    "name": name,
                },
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    url,
                    headers={**self._headers(), "Accept": "application/json, text/event-stream"},
                    json=payload,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("result", {}).get("content", [])
                    if content and isinstance(content, list) and content[0].get("text"):
                        raw_text = content[0]["text"]
                        try:
                            parsed = json.loads(raw_text)
                            return DealAnalysis(**parsed, raw=parsed)
                        except Exception:
                            pass
        except Exception:
            pass

        fallback_url = f"{self.api_base}/api/v1/public/analyse"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                fallback_url,
                headers=self._headers(),
                json={"transcript": transcript_clean, "name": name},
            )
            resp.raise_for_status()
            res_json = resp.json()
            data = res_json.get("data") or res_json
            return DealAnalysis(**data, raw=data)

    # -------------------------------------------------------------------------
    # Saved Deals & Workspace Actions (Requires Auth)
    # -------------------------------------------------------------------------

    def get_deal_health(self, deal_id: str) -> Dict[str, Any]:
        """Assess 0-100 health score for a saved deal in Revtelic."""
        return self._call_tool_sync("get_deal_health", {"deal_id": deal_id})

    def get_deal_risks(self, deal_id: str) -> Dict[str, Any]:
        """Identify critical hidden blockers and deal risks."""
        return self._call_tool_sync("get_deal_risks", {"deal_id": deal_id})

    def get_stakeholders(self, deal_id: str) -> Dict[str, Any]:
        """Assess champion strength, economic buyer access, and missing contacts."""
        return self._call_tool_sync("get_stakeholders", {"deal_id": deal_id})

    def get_next_best_action(self, deal_id: str) -> Dict[str, Any]:
        """Determine highest-priority action to progress or close the deal."""
        return self._call_tool_sync("get_next_best_action", {"deal_id": deal_id})

    def list_deals(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List active dealboards from the connected Revtelic workspace."""
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        url = f"{self.api_base}/api/integrations/v1/dealboards"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._headers(), params=params)
            resp.raise_for_status()
            data = resp.json().get("data") or {}
            return data.get("dealboards", []) if isinstance(data, dict) else data

    def _call_tool_sync(self, name: str, args: Dict[str, Any]) -> Any:
        url = f"{self.api_base}/api/v1/mcp"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": args},
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url,
                headers={**self._headers(), "Accept": "application/json, text/event-stream"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise RuntimeError(data["error"].get("message") or data["error"])
            content = data.get("result", {}).get("content", [])
            if content and isinstance(content, list) and content[0].get("text"):
                try:
                    return json.loads(content[0]["text"])
                except Exception:
                    return content[0]["text"]
            return data.get("result")
