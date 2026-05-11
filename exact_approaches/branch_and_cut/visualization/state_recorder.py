"""
State Recorder for Branch & Cut Algorithm.
Records intermediate states during the search (route progression, decisions, metrics).
Enables real-time and replay visualization of the algorithm's evolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AlgorithmStep:
    """One intermediate state during algorithm execution."""
    step_number: int
    action: str  # "initialize", "add_node", "close_route", "prune", "update_incumbent"
    route: list[int]
    current_profit: float
    current_cost: float
    remaining_budget: float
    nodes_explored: int
    nodes_pruned: int
    decision_reason: str = ""
    candidate_nodes: list[int] = field(default_factory=list)
    best_incumbent_profit: float = 0.0


class StateRecorder:
    """Records algorithm progression for visualization."""

    def __init__(self, enable_recording: bool = True) -> None:
        self.enable_recording = enable_recording
        self.steps: list[AlgorithmStep] = []
        self.step_counter = 0

    def record_step(
        self,
        action: str,
        route: list[int],
        current_profit: float,
        current_cost: float,
        remaining_budget: float,
        nodes_explored: int,
        nodes_pruned: int,
        decision_reason: str = "",
        candidate_nodes: list[int] | None = None,
        best_incumbent_profit: float = 0.0,
    ) -> None:
        """Record one algorithm step."""
        if not self.enable_recording:
            return

        self.step_counter += 1
        step = AlgorithmStep(
            step_number=self.step_counter,
            action=action,
            route=list(route),
            current_profit=current_profit,
            current_cost=current_cost,
            remaining_budget=remaining_budget,
            nodes_explored=nodes_explored,
            nodes_pruned=nodes_pruned,
            decision_reason=decision_reason,
            candidate_nodes=candidate_nodes or [],
            best_incumbent_profit=best_incumbent_profit,
        )
        self.steps.append(step)

    def to_dict(self) -> dict[str, Any]:
        """Convert recorded steps to a dict for JSON serialization."""
        return {
            "total_steps": len(self.steps),
            "steps": [
                {
                    "step_number": step.step_number,
                    "action": step.action,
                    "route": step.route,
                    "current_profit": step.current_profit,
                    "current_cost": step.current_cost,
                    "remaining_budget": step.remaining_budget,
                    "nodes_explored": step.nodes_explored,
                    "nodes_pruned": step.nodes_pruned,
                    "decision_reason": step.decision_reason,
                    "candidate_nodes": step.candidate_nodes,
                    "best_incumbent_profit": step.best_incumbent_profit,
                }
                for step in self.steps
            ],
        }
