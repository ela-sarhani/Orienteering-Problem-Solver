"""Tabu Search solver for the Orienteering Problem."""

from __future__ import annotations

from dataclasses import dataclass
import random
import time

from exact_approaches.common.op_instance import OPInstance
from exact_approaches.common.solution import OPSolution
from metaheuristic_approaches.common.route_utils import greedy_closed_route, random_feasible_route
from metaheuristic_approaches.common.state_recorder import StateRecorder

from .heuristics import generate_neighbors, initial_route, route_signature


@dataclass(slots=True)
class TabuSearchConfig:
    max_iterations: int = 90
    tenure: int = 7


class TabuSearchSolver:
    def __init__(self, config: TabuSearchConfig | None = None) -> None:
        self.config = config or TabuSearchConfig()
        self._recorder = StateRecorder(enable_recording=True)

    def solve(self, instance: OPInstance) -> OPSolution:
        rng = random.Random(23)
        self._recorder = StateRecorder(enable_recording=True)
        start_time = time.perf_counter()

        initial_candidates: list[list[int]] = []
        greedy_route, _, _ = greedy_closed_route(instance)
        initial_candidates.append(list(greedy_route))
        for _ in range(12):
            candidate = random_feasible_route(instance, rng)
            if candidate not in initial_candidates:
                initial_candidates.append(candidate)

        best_initial_route = max(
            initial_candidates,
            key=lambda route: (instance.route_profit(route), -instance.route_cost(route)),
        )
        current_route = list(best_initial_route)
        current_profit = instance.route_profit(current_route)
        current_cost = instance.route_cost(current_route)
        best_route = list(current_route)
        best_profit = current_profit
        best_cost = current_cost

        tabu_expiration: dict[int, int] = {}
        candidate_evaluations = 0
        iterations_completed = 0

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

        for iteration in range(1, self.config.max_iterations + 1):
            iterations_completed = iteration
            neighbors = generate_neighbors(instance, current_route)
            candidate_evaluations += len(neighbors)
            if not neighbors:
                self._recorder.record_step(
                    action="prune",
                    route=current_route,
                    current_profit=current_profit,
                    current_cost=current_cost,
                    remaining_budget=instance.budget - current_cost,
                    iterations=iteration,
                    candidate_evaluations=candidate_evaluations,
                    decision_reason="no admissible neighbors found",
                    best_incumbent_profit=best_profit,
                )
                break

            chosen = None
            chosen_reason = ""
            for neighbor in neighbors:
                node = neighbor.node
                is_tabu = tabu_expiration.get(node, 0) > iteration
                profit = instance.route_profit(neighbor.route)
                cost = instance.route_cost(neighbor.route)
                if cost > instance.budget:
                    continue
                if is_tabu and profit <= best_profit:
                    continue
                chosen = neighbor
                chosen_reason = f"{neighbor.action} node {node}"
                break

            if chosen is None:
                chosen = neighbors[0]
                chosen_reason = f"aspiration move {chosen.action} node {chosen.node}"

            current_route = list(chosen.route)
            current_profit = instance.route_profit(current_route)
            current_cost = instance.route_cost(current_route)
            tabu_expiration[chosen.node] = iteration + self.config.tenure

            self._recorder.record_step(
                action="iteration",
                route=current_route,
                current_profit=current_profit,
                current_cost=current_cost,
                remaining_budget=instance.budget - current_cost,
                iterations=iteration,
                candidate_evaluations=candidate_evaluations,
                decision_reason=chosen_reason,
                candidate_nodes=[neighbor.node for neighbor in neighbors[:5]],
                best_incumbent_profit=best_profit,
            )

            if current_profit > best_profit or (current_profit == best_profit and current_cost < best_cost):
                best_route = list(current_route)
                best_profit = current_profit
                best_cost = current_cost
                self._recorder.record_step(
                    action="update_incumbent",
                    route=best_route,
                    current_profit=best_profit,
                    current_cost=best_cost,
                    remaining_budget=instance.budget - best_cost,
                    iterations=iteration,
                    candidate_evaluations=candidate_evaluations,
                    decision_reason=f"improved incumbent after iteration {iteration}",
                    best_incumbent_profit=best_profit,
                )

        runtime = time.perf_counter() - start_time
        return OPSolution(
            route=best_route,
            total_profit=best_profit,
            total_cost=best_cost,
            feasible=best_cost <= instance.budget,
            method="tabu_search",
            nodes_explored=iterations_completed,
            pruned_nodes=max(0, candidate_evaluations - iterations_completed),
            runtime_seconds=runtime,
            metadata={
                "algorithm": "tabu_search",
                "state_history": self._recorder.to_dict(),
                "best_route_signature": route_signature(best_route),
            },
        )
