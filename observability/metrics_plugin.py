from collections import defaultdict
from typing import Dict, Any, Optional
from datetime import datetime
import json

class MetricsPlugin:

    """
    A lightweight custom metrics collector for observability.

    This plugin collects:
    - keyword_turns: how many times the keywords_agent interacted
    - retrieved_papers: how many papers were retrieved by retrieval_agent
    - foresee_used: whether foresee_agent was triggered
    """

    def __init__(self):
        self.data = defaultdict(int)
        self.used_foresee = False

    # -------------------------------
    # Phase 1: Keywords Agent
    # -------------------------------
    def on_keywords_event(self, event: Any) -> None:
        """Called whenever keywords_agent produces an event"""
        self.data["keywords_turns"] += 1

    # -------------------------------
    # Phase 2: Retrieval Agent
    # -------------------------------
    def on_retrieval_tool(self, tool_response: Any) -> None:
        """Capture tool output from retrieve_papers."""
        output = getattr(tool_response, "output", None) or {}
        total = output.get("total")
        if isinstance(total, int):
            self.data["retrieved_papers"] = total

    # -------------------------------
    # Phase 3: Foresee Agent
    # -------------------------------
    def mark_foresee_used(self) -> str:
        """Flag that foresee_agent has been invoked."""
        self.used_foresee = True

    # -------------------------------
    # Summary (for prininting and saving)
    # -------------------------------
    def summary(self) -> str:
        return (
            f" Metric Summary:\n"
            f"- Keyword refinement turns: {self.data.get('keywords_turns', 0)}\n"
            f"- Retrieved papers: {self.data.get('retrieved_papers', 0)}\n"
            f"- Foresee agent used: {'yes' if self.used_foresee else 'no'}"

        )

    def to_dict(self, session_id: str) -> Dict[str, Any]:
        return {
            "session_id": session_id,
            "tempstamp": datetime.utcnow().isoformat(),
            "keywords_turns": self.data.get("keywords_turns", 0),
            "retrieved_papers": self.data.get("retrieved_papers", 0),
            "foresee_used": self.used_foresee,
        }

    def persist(self, session_id: str, path: str = "metrics.jsonl") -> None:
        record = self.do_dict(session_id)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")