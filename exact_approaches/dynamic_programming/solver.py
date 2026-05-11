"""
Dynamic Programming Solver for OP.
Uses state-space DP with memoization to explore all possible routes.
State: (current_node, visited_nodes_bitmask, remaining_budget)
Computes maximum profit achievable from each state.
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional
import time
from functools import lru_cache

from exact_approaches.common.op_instance import OPInstance
from exact_approaches.common.solution import OPSolution
from .visualization.state_recorder import StateRecorder

from .heuristics import greedy_closed_route


class DynamicProgrammingSolver:
    """Dynamic programming solver for the Orienteering Problem using bitmask DP."""

    def __init__(self) -> None:
        self.nodes_explored = 0
        self.pruned_nodes = 0
        self._best_solution: OPSolution | None = None
        self._instance: OPInstance | None = None
        self._eps = 1e-12
        self._recorder = StateRecorder(enable_recording=True)
        self._memo: Dict[Tuple[int, int, float], Tuple[float, list[int]]] = {}
        self._step_counter = 0

    def solve(self, instance: OPInstance) -> OPSolution:
        self._instance = instance
        self.nodes_explored = 0
        self.pruned_nodes = 0
        self._recorder = StateRecorder(enable_recording=True)
        self._memo = {}
        self._step_counter = 0
        start_time = time.perf_counter()

        # Initialize with greedy solution
        greedy_route, greedy_profit, greedy_cost = greedy_closed_route(instance)
        self._best_solution = OPSolution(
            route=greedy_route,
            total_profit=greedy_profit,
            total_cost=greedy_cost,
            feasible=greedy_cost <= instance.budget + self._eps,
            method="dynamic_programming",
            nodes_explored=0,
            pruned_nodes=0,
            runtime_seconds=0.0,
            metadata={"incumbent_source": "greedy"},
        )

        # Start DP from depot with all nodes unvisited
        initial_visited = 1  # Only depot (node 0) is visited (bit 0 set)
        best_profit, best_route = self._dp_solve(
            current_node=instance.start,
            visited_mask=initial_visited,
            remaining_budget=instance.budget,
            path=[instance.start],
        )

        # Ensure best route is closed
        if best_route and best_route[-1] != instance.start:
            best_route.append(instance.start)

        if best_route:
            best_cost = instance.route_cost(best_route)
            if best_cost <= instance.budget + self._eps and best_profit > self._best_solution.total_profit - self._eps:
                self._best_solution = OPSolution(
                    route=best_route,
                    total_profit=best_profit,
                    total_cost=best_cost,
                    feasible=best_cost <= instance.budget + self._eps,
                    method="dynamic_programming",
                    nodes_explored=self.nodes_explored,
                    pruned_nodes=self.pruned_nodes,
                    runtime_seconds=0.0,
                    metadata={"incumbent_source": "dp_exploration"},
                )

        runtime = time.perf_counter() - start_time
        assert self._best_solution is not None
        self._best_solution.nodes_explored = self.nodes_explored
        self._best_solution.pruned_nodes = self.pruned_nodes
        self._best_solution.runtime_seconds = runtime
        self._best_solution.metadata = {
            **self._best_solution.metadata,
            "algorithm": "dynamic_programming_bitmask",
            "state_history": self._recorder.to_dict(),
        }
        return self._best_solution

    def _dp_solve(
        self,
        current_node: int,
        visited_mask: int,
        remaining_budget: float,
        path: list[int],
    ) -> Tuple[float, list[int]]:
        """Recursive DP solver with memoization."""
        assert self._instance is not None
        self.nodes_explored += 1
        
        # Create state key for memoization (use quantized budget to reduce states)
        budget_key = int(remaining_budget * 100)  # Quantize to 0.01 precision
        state_key = (current_node, visited_mask, budget_key)

        if state_key in self._memo:
            profit, route = self._memo[state_key]
            return profit, list(route)

        # Try closing the route (return to start)
        close_cost = self._instance.distance(current_node, self._instance.start)
        current_profit = self._compute_path_profit(path)

        best_profit = current_profit
        best_route = list(path)

        # Record current state as a "step"
        self._step_counter += 1
        self._recorder.record_step(
            action="dp_state",
            route=list(path),
            current_profit=current_profit,
            current_cost=self._instance.route_cost(list(path) + [self._instance.start]),
            remaining_budget=remaining_budget,
            nodes_explored=self.nodes_explored,
            nodes_pruned=self.pruned_nodes,
            decision_reason=f"visited_mask={visited_mask:b}, current={current_node}",
            best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
        )

        # If we can close and it's feasible
        if close_cost <= remaining_budget + self._eps:
            if current_profit > best_profit - self._eps:
                best_profit = current_profit
                best_route = list(path) + [self._instance.start]

        # Try adding each unvisited node
        for node in range(self._instance.n):
            if node == self._instance.start:
                continue

            # Check if node already visited
            if visited_mask & (1 << node):
                continue

            edge_cost = self._instance.distance(current_node, node)
            new_budget = remaining_budget - edge_cost

            # Prune if not enough budget
            if new_budget < -self._eps:
                self.pruned_nodes += 1
                self._recorder.record_step(
                    action="prune",
                    route=list(path),
                    current_profit=current_profit,
                    current_cost=self._instance.route_cost(list(path) + [self._instance.start]),
                    remaining_budget=remaining_budget,
                    nodes_explored=self.nodes_explored,
                    nodes_pruned=self.pruned_nodes,
                    decision_reason=f"edge to node {node} exceeds budget",
                    candidate_nodes=[node],
                    best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
                )
                continue

            # Recursive call
            new_mask = visited_mask | (1 << node)
            new_path = list(path) + [node]
            profit, route = self._dp_solve(
                current_node=node,
                visited_mask=new_mask,
                remaining_budget=new_budget,
                path=new_path,
            )

            if profit > best_profit - self._eps:
                best_profit = profit
                best_route = route

        # Memoize result
        self._memo[state_key] = (best_profit, best_route)
        return best_profit, best_route

    def _compute_path_profit(self, path: list[int]) -> float:
        """Compute total profit of a path."""
        assert self._instance is not None
        total = sum(self._instance.profits[node] for node in path if node != self._instance.start)
        return total
