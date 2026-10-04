"""
risk_register.py
Structured Security Risk Register for the Digital Banking System hybrid-cloud simulation.
Encapsulates simulation-level governance risks R1 through R6:
- R1: Unauthorized internal access to core banking subsystems
- R2: Sensitive data routed to public cloud tier
- R3: Cloud provider dependency and control risk
- R4: Key-management / cryptographic failure
- R5: Availability / service outage risk
- R6: Data residency and cross-border governance risk

Scoring formula: Risk Score = Likelihood × Impact (1 to 25).
Note: This is an academic simulation abstraction and does not claim to reproduce
the FAHP + Dempster-Shafer method from literature.
"""

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SecurityRisk:
    risk_id: str
    category: str
    title: str
    description: str
    likelihood: int
    impact: int
    risk_score: int
    risk_level: str
    mitigation: str
    monitoring_indicator: str

    def validate(self) -> bool:
        """Validates that Likelihood, Impact, and Risk Score obey mathematical constraints."""
        if not (1 <= self.likelihood <= 5):
            return False
        if not (1 <= self.impact <= 5):
            return False
        if self.risk_score != self.likelihood * self.impact:
            return False
        return True


class RiskRegister:
    """Manages project-level security risk definitions, scoring invariants, and reporting."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Default to standard project config location
            root_dir = Path(__file__).resolve().parent.parent.parent
            config_path = root_dir / "config" / "security_risk_register.json"

        self.config_path = Path(config_path)
        self.risks: Dict[str, SecurityRisk] = {}
        self.raw_data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Loads and parses the JSON risk register file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Security risk register not found at: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        for item in self.raw_data.get("risks", []):
            risk = SecurityRisk(
                risk_id=item["risk_id"],
                category=item["category"],
                title=item["title"],
                description=item["description"],
                likelihood=int(item["likelihood"]),
                impact=int(item["impact"]),
                risk_score=int(item["risk_score"]),
                risk_level=item["risk_level"],
                mitigation=item["mitigation"],
                monitoring_indicator=item["monitoring_indicator"]
            )
            if not risk.validate():
                raise ValueError(
                    f"Invalid scoring for risk {risk.risk_id}: likelihood={risk.likelihood}, "
                    f"impact={risk.impact}, score={risk.risk_score}"
                )
            self.risks[risk.risk_id] = risk

    def get_risk(self, risk_id: str) -> Optional[SecurityRisk]:
        """Retrieves a risk by identifier (e.g. 'R1')."""
        return self.risks.get(risk_id)

    def get_all_risks(self) -> List[SecurityRisk]:
        """Returns all configured security risks."""
        return list(self.risks.values())

    def get_risks_by_level(self, level: str) -> List[SecurityRisk]:
        """Filters risks by level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')."""
        target = level.upper()
        return [r for r in self.risks.values() if r.risk_level == target]

    def validate_scoring_invariants(self) -> bool:
        """Verifies that every loaded risk obeys the mathematical scoring formula."""
        return all(r.validate() for r in self.risks.values())

    def to_markdown_table(self) -> str:
        """Renders an executive Markdown table of the risk register."""
        lines = [
            "| Risk ID | Category | Title | Likelihood (1-5) | Impact (1-5) | Score (L×I) | Level | Mitigation |",
            "| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |"
        ]
        for r in self.risks.values():
            lines.append(
                f"| **{r.risk_id}** | `{r.category}` | {r.title} | {r.likelihood} | {r.impact} | "
                f"**{r.risk_score}** | `{r.risk_level}` | {r.mitigation[:60]}... |"
            )
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Returns dictionary representation."""
        return {
            "project": self.raw_data.get("project"),
            "disclaimer": self.raw_data.get("disclaimer"),
            "total_risks": len(self.risks),
            "risks": [asdict(r) for r in self.risks.values()]
        }
