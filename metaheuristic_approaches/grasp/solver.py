"""GRASP solver for the Orienteering Problem."""

from __future__ import annotations

from dataclasses import dataclass
import random
import time

from exact_approaches.common.op_instance import OPInstance
from exact_approaches.common.solution import OPSolution
from metaheuristic_approaches.common.route_utils import greedy_closed_route
from metaheuristic_approaches.common.state_recorder import StateRecorder

from .heuristics import construct_route, local_search


@dataclass(slots=True)
class GraspConfig:
    iterations: int = 70
    alpha: float = 0.35
    seed: int = 13


class GraspSolver:
    def __init__(self, config: GraspConfig | None = None) -> None:
        self.config = config or GraspConfig()
        self._recorder = StateRecorder(enable_recording=True)

    def solve(self, instance: OPInstance) -> OPSolution:
        rng = random.Random(self.config.seed)
        self._recorder = StateRecorder(enable_recording=True)
        start_time = time.perf_counter()

        greedy_route, greedy_profit, greedy_cost = greedy_closed_route(instance)
        best_route = list(greedy_route)
        best_profit = greedy_profit
        best_cost = greedy_cost
        candidate_evaluations = 0

        self._recorder.record_step(
            action="initialize",
            route=best_route,
            current_profit=best_profit,
            current_cost=best_cost,
            remaining_budget=instance.budget - best_cost,
            iterations=0,
            candidate_evaluations=0,
            decision_reason="greedy incumbent initialized",
            best_incumbent_profit=best_profit,
        )

        for iteration in range(1, self.config.iterations + 1):
            constructed_route, construct_evals = construct_route(instance, rng, self.config.alpha)
            local_route, local_evals = local_search(instance, constructed_route)
            candidate_evaluations += construct_evals + local_evals

            local_profit = instance.route_profit(local_route)
            local_cost = instance.route_cost(local_route)

            self._recorder.record_step(
                action="iteration",
                route=local_route,
                current_profit=local_profit,
                current_cost=local_cost,
                remaining_budget=instance.budget - local_cost,
                iterations=iteration,
                candidate_evaluations=candidate_evaluations,
                decision_reason=f"construction + local search with alpha={self.config.alpha}",
                best_incumbent_profit=best_profit,
            )

            if local_profit > best_profit or (local_profit == best_profit and local_cost < best_cost):
                best_route = list(local_route)
                best_profit = local_profit
                best_cost = local_cost
                self._recorder.record_step(
                    action="update_incumbent",
                    route=best_route,
                    current_profit=best_profit,
                    current_cost=best_cost,
                    remaining_budget=instance.budget - best_cost,
                    iterations=iteration,
                    candidate_evaluations=candidate_evaluations,
                    decision_reason=f"new best route found in GRASP iteration {iteration}",
                    best_incumbent_profit=best_profit,
                )

        runtime = time.perf_counter() - start_time
        return OPSolution(
            route=best_route,
            total_profit=best_profit,
            total_cost=best_cost,
            feasible=best_cost <= instance.budget,
            method="grasp",
            nodes_explored=self.config.iterations,
            pruned_nodes=max(0, candidate_evaluations - self.config.iterations),
            runtime_seconds=runtime,
            metadata={
                "algorithm": "grasp",
                "state_history": self._recorder.to_dict(),
            },
        )
