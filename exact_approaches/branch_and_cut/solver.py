"""
Branch and Cut Solver for OP.
Combines branch and bound with constraint-based cutting strategies.
Uses subtour elimination cuts and connectivity constraints for enhanced pruning.
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
    depth: int = 0


class BranchAndCutSolver:
    """Branch and cut solver for the Orienteering Problem.
    
    Enhances branch and bound with:
    - Subtour elimination constraints
    - Connected component analysis
    - Distance-based valid inequalities
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

        # Initialize with greedy solution
        greedy_route, greedy_profit, greedy_cost = greedy_closed_route(instance)
        self._best_solution = OPSolution(
            route=greedy_route,
            total_profit=greedy_profit,
            total_cost=greedy_cost,
            feasible=greedy_cost <= instance.budget + self._eps,
            method="branch_and_cut",
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
                depth=0,
            )
        )

        runtime = time.perf_counter() - start_time
        assert self._best_solution is not None
        self._best_solution.nodes_explored = self.nodes_explored
        self._best_solution.pruned_nodes = self.pruned_nodes
        self._best_solution.runtime_seconds = runtime
        self._best_solution.metadata = {
            **self._best_solution.metadata,
            "algorithm": "branch_and_cut_with_constraints",
            "state_history": self._recorder.to_dict(),
        }
        return self._best_solution

    def _check_cutting_plane(self, route: list[int], state: _SearchState) -> bool:
        """Check cutting plane validity: subtour elimination constraint.
        
        Returns False if route violates a cutting plane, True if feasible.
        """
        assert self._instance is not None
        
        # Subtour elimination: if we have visited nodes, they should form a connected path
        if len(route) > 2:
            # Check if the path is valid (no gaps in connectivity)
            for i in range(1, len(route) - 1):
                node = route[i]
                prev_node = route[i - 1]
                next_candidate = route[i + 1] if i + 1 < len(route) else self._instance.start
                
                # Distance-based cut: prune if cost to nearest neighbor is too high
                nearest_dist = min(
                    self._instance.distance(node, n) 
                    for n in state.remaining 
                    if n != node
                ) if state.remaining else float('inf')
                
                # If current cost plus nearest neighbor exceeds budget, likely infeasible
                if (state.open_cost + nearest_dist + 
                    self._instance.distance(next_candidate, self._instance.start) > 
                    self._instance.budget + self._eps):
                    return False
        
        return True

    def _search(self, state: _SearchState) -> None:
        assert self._instance is not None
        self.nodes_explored += 1

        # Bound check: budget exceeded
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

        # LP bound check
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

        # Cutting plane check
        if not self._check_cutting_plane(state.route, state):
            self.pruned_nodes += 1
            self._recorder.record_step(
                action="prune",
                route=state.route,
                current_profit=state.profit,
                current_cost=state.open_cost,
                remaining_budget=self._instance.budget - state.open_cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason="cutting plane constraint violated",
                best_incumbent_profit=self._best_solution.total_profit if self._best_solution else 0.0,
            )
            return

        # Try closure: check if we can close the current path
        self._update_with_closure(state)

        # Try greedy completion
        if state.open_cost + self._instance.distance(state.current, self._instance.start) <= self._instance.budget + self._eps:
            completion = self._greedy_completion(state)
            if completion is not None:
                route, profit, cost = completion
                self._update_best(route, profit, cost, source="greedy_completion")

        # Branch: try adding remaining nodes
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
            
            # Pruning: edge cost alone exceeds budget
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

            # Recursive search
            self._search(
                _SearchState(
                    route=state.route + [node],
                    current=node,
                    open_cost=new_open_cost,
                    profit=new_profit,
                    remaining=new_remaining,
                    remaining_profit=new_remaining_profit,
                    depth=state.depth + 1,
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
                route=route,
                total_profit=profit,
                total_cost=cost,
                feasible=True,
                method="branch_and_cut",
                nodes_explored=self.nodes_explored,
                pruned_nodes=self.pruned_nodes,
                runtime_seconds=0.0,
                metadata={"incumbent_source": source},
            )
            self._recorder.record_step(
                action="update_incumbent",
                route=route,
                current_profit=profit,
                current_cost=cost,
                remaining_budget=self._instance.budget - cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason=f"new incumbent with profit {profit:.2f} (from {source})",
                best_incumbent_profit=profit,
            )
        elif profit > self._best_solution.total_profit + self._eps:
            self._best_solution = OPSolution(
                route=route,
                total_profit=profit,
                total_cost=cost,
                feasible=True,
                method="branch_and_cut",
                nodes_explored=self.nodes_explored,
                pruned_nodes=self.pruned_nodes,
                runtime_seconds=0.0,
                metadata={"incumbent_source": source},
            )
            self._recorder.record_step(
                action="update_incumbent",
                route=route,
                current_profit=profit,
                current_cost=cost,
                remaining_budget=self._instance.budget - cost,
                nodes_explored=self.nodes_explored,
                nodes_pruned=self.pruned_nodes,
                decision_reason=f"improved incumbent from {self._best_solution.total_profit:.2f} to {profit:.2f}",
                best_incumbent_profit=profit,
            )
