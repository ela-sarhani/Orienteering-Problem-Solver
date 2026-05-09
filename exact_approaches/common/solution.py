"""
OP Solution Container.
Stores solver results (route, profit, cost, feasibility, runtime, stats).
Handles serialization to JSON with full visualization payload.
Used by all solvers (exact and heuristic) to format and export their results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any

from .op_instance import OPInstance


@dataclass(slots=True)
class OPSolution:
    route: list[int]
    total_profit: float
    total_cost: float
    feasible: bool
    method: str = "branch_and_bound"
    nodes_explored: int = 0
    pruned_nodes: int = 0
    runtime_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def visited_nodes(self) -> list[int]:
        return self.route[1:-1] if len(self.route) >= 2 else []

    def to_dict(self, instance: OPInstance) -> dict[str, Any]:
        return {
            "method": self.method,
            "feasible": self.feasible,
            "route": self.route,
            "visited_nodes": self.visited_nodes,
            "total_profit": self.total_profit,
            "total_cost": self.total_cost,
            "budget": instance.budget,
            "nodes_explored": self.nodes_explored,
            "pruned_nodes": self.pruned_nodes,
            "runtime_seconds": round(self.runtime_seconds, 6),
            "metadata": self.metadata,
            "visualization": instance.visualisation_payload(self.route),
        }

    def to_json(self, path: str | Path, instance: OPInstance) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(instance), indent=2), encoding="utf-8")
