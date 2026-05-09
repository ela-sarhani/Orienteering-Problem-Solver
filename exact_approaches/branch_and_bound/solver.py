"""
Branch and Bound Solver for OP.
Implements depth-first B&B search over partial routes.
Prunes branches when they cannot improve the incumbent or exceed the budget.
Core algorithm: explores partial routes, tries completions, updates incumbent.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable

from exact_approaches.common.op_instance import OPInstance
from exact_approaches.common.solution import OPSolution
from .visualization.state_recorder import StateRecorder

from .heuristics import greedy_closed_route


@dataclass(slots=True)
class _SearchState:
    route: list[int]
    current: int
    open_cost: float
    profit: float
    remaining: frozenset[int]
    remaining_profit: float


class BranchAndBoundSolver:
    """Depth-first branch and bound solver for the Orienteering Problem.

    The search tree enumerates simple open paths starting from the depot.
    A solution is feasible once the path is closed by returning to the start.
    """

    def __init__(self) -> None:
        self.nodes_explored = 0
        self.pruned_nodes = 0
        self._best_solution: OPSolution | None = None
        self._instance: OPInstance | None = None
        self._eps = 1e-12
        self._recorder = StateRecorder(enable_recording=True)

    def solve(self, instance: OPInstance) -> OPSolution:
        self._instance = instance
        self.nodes_explored = 0
        self.pruned_nodes = 0
        self._recorder = StateRecorder(enable_recording=True)
        start_time = time.perf_counter()

        greedy_route, greedy_profit, greedy_cost = greedy_closed_route(instance)
        self._best_solution = OPSolution(
            route=greedy_route,
            total_profit=greedy_profit,
            total_cost=greedy_cost,
            feasible=greedy_cost <= instance.budget + self._eps,
            method="branch_and_bound",
            nodes_explored=0,
            pruned_nodes=0,
            runtime_seconds=0.0,
            metadata={"incumbent_source": "greedy"},
        )

        initial_remaining = frozenset(range(instance.n)) - {instance.start}
        initial_remaining_profit = sum(instance.profits[node] for node in initial_remaining)

        self._search(
            _SearchState(
                route=[instance.start],
                current=instance.start,
                open_cost=0.0,
                profit=0.0,
                remaining=initial_remaining,
                remaining_profit=initial_remaining_profit,
            )
        )

        runtime = time.perf_counter() - start_time
        assert self._best_solution is not None
        self._best_solution.nodes_explored = self.nodes_explored
        self._best_solution.pruned_nodes = self.pruned_nodes
        self._best_solution.runtime_seconds = runtime
        self._best_solution.metadata = {
            **self._best_solution.metadata,
            "algorithm": "depth_first_branch_and_bound",
            "state_history": self._recorder.to_dict(),
        }
        return self._best_solution

    def _search(self, state: _SearchState) -> None:
        assert self._instance is not None
        self.nodes_explored += 1

        if state.open_cost > self._instance.budget + self._eps:
            self.pruned_nodes += 1
            self._recorder.record_step(
                action="prune",
                route=state.route,
                current_profit=state.profit,
                current_cost=state.open_cost,
                remaining_budget=self._instance.budget - state.open_cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason="budget exceeded",
                best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
            )
            return

        if self._best_solution is not None:
            optimistic_profit = state.profit + state.remaining_profit
            if optimistic_profit <= self._best_solution.total_profit + self._eps:
                self.pruned_nodes += 1
                self._recorder.record_step(
                    action="prune",
                    route=state.route,
                    current_profit=state.profit,
                    current_cost=state.open_cost,
                    remaining_budget=self._instance.budget - state.open_cost,
                    nodes_explored=self.nodes_explored,
                    nodes_pruned=self.pruned_nodes,
                    decision_reason=f"optimistic profit {optimistic_profit:.2f} <= incumbent {self._best_solution.total_profit:.2f}",
                    best_incumbent_profit=self._best_solution.total_profit,
                )
                return

        self._update_with_closure(state)

        if state.open_cost + self._instance.distance(state.current, self._instance.start) <= self._instance.budget + self._eps:
            completion = self._greedy_completion(state)
            if completion is not None:
                route, profit, cost = completion
                self._update_best(route, profit, cost, source="greedy_completion")

        ordered_candidates = sorted(
            state.remaining,
            key=lambda node: (
                -self._instance.profits[node],
                self._instance.distance(state.current, node),
                node,
            ),
        )

        for node in ordered_candidates:
            edge_cost = self._instance.distance(state.current, node)
            new_open_cost = state.open_cost + edge_cost
            if new_open_cost > self._instance.budget + self._eps:
                self.pruned_nodes += 1
                self._recorder.record_step(
                    action="prune",
                    route=state.route,
                    current_profit=state.profit,
                    current_cost=state.open_cost,
                    remaining_budget=self._instance.budget - state.open_cost,
                    nodes_explored=self.nodes_explored,
                    nodes_pruned=self.pruned_nodes,
                    decision_reason=f"edge to node {node} exceeds budget",
                    candidate_nodes=[node],
                    best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
                )
                continue

            new_remaining = state.remaining - {node}
            new_profit = state.profit + self._instance.profits[node]
            new_remaining_profit = state.remaining_profit - self._instance.profits[node]

            self._recorder.record_step(
                action="add_node",
                route=state.route + [node],
                current_profit=new_profit,
                current_cost=new_open_cost,
                remaining_budget=self._instance.budget - new_open_cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason=f"add node {node} (profit={self._instance.profits[node]}, edge_cost={edge_cost:.2f})",
                best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
            )

            self._search(
                _SearchState(
                    route=state.route + [node],
                    current=node,
                    open_cost=new_open_cost,
                    profit=new_profit,
                    remaining=new_remaining,
                    remaining_profit=new_remaining_profit,
                )
            )

    def _update_with_closure(self, state: _SearchState) -> None:
        assert self._instance is not None
        total_cost = state.open_cost + self._instance.distance(state.current, self._instance.start)
        if total_cost <= self._instance.budget + self._eps:
            closed_route = state.route + [self._instance.start]
            self._update_best(closed_route, state.profit, total_cost, source="closed_now")

    def _greedy_completion(self, state: _SearchState) -> tuple[list[int], float, float] | None:
        assert self._instance is not None
        route = list(state.route)
        current = state.current
        open_cost = state.open_cost
        profit = state.profit
        remaining = set(state.remaining)

        while remaining:
            best_node = None
            best_key = None
            current_to_start = self._instance.distance(current, self._instance.start)

            for node in remaining:
                candidate_open_cost = open_cost + self._instance.distance(current, node)
                candidate_total_cost = candidate_open_cost + self._instance.distance(node, self._instance.start)
                if candidate_total_cost > self._instance.budget + self._eps:
                    continue

                additional_closed_cost = candidate_total_cost - (open_cost + current_to_start)
                node_profit = self._instance.profits[node]
                if additional_closed_cost <= self._eps:
                    key = (1, node_profit, -additional_closed_cost, -node)
                else:
                    key = (0, node_profit / additional_closed_cost, node_profit, -additional_closed_cost, -node)

                if best_key is None or key > best_key:
                    best_key = key
                    best_node = node

            if best_node is None:
                break

            open_cost += self._instance.distance(current, best_node)
            profit += self._instance.profits[best_node]
            route.append(best_node)
            current = best_node
            remaining.remove(best_node)

        total_cost = open_cost + self._instance.distance(current, self._instance.start)
        if total_cost > self._instance.budget + self._eps:
            return None

        route.append(self._instance.start)
        return route, profit, total_cost

    def _update_best(self, route: list[int], profit: float, cost: float, source: str) -> None:
        assert self._instance is not None
        if cost > self._instance.budget + self._eps:
            return

        if self._best_solution is None:
            self._best_solution = OPSolution(
                route=list(route),
                total_profit=profit,
                total_cost=cost,
                feasible=True,
                method="branch_and_bound",
                nodes_explored=self.nodes_explored,
                pruned_nodes=self.pruned_nodes,
                runtime_seconds=0.0,
                metadata={"incumbent_source": source},
            )
            self._recorder.record_step(
                action="update_incumbent",
                route=list(route),
                current_profit=profit,
                current_cost=cost,
                remaining_budget=self._instance.budget - cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason=f"initial incumbent from {source}",
                best_incumbent_profit=profit,
            )
            return

        better_profit = profit > self._best_solution.total_profit + self._eps
        better_cost = abs(profit - self._best_solution.total_profit) <= self._eps and cost < self._best_solution.total_cost - self._eps
        if better_profit or better_cost:
            self._best_solution = OPSolution(
                route=list(route),
                total_profit=profit,
                total_cost=cost,
                feasible=True,
                method="branch_and_bound",
                nodes_explored=self.nodes_explored,
                pruned_nodes=self.pruned_nodes,
                runtime_seconds=0.0,
                metadata={"incumbent_source": source},
            )
            self._recorder.record_step(
                action="update_incumbent",
                route=list(route),
                current_profit=profit,
                current_cost=cost,
                remaining_budget=self._instance.budget - cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason=f"improved incumbent from {source}",
                best_incumbent_profit=profit,
            )
