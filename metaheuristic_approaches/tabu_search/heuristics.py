"""Helper functions for the Tabu Search approach."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from exact_approaches.common.op_instance import OPInstance
from metaheuristic_approaches.common.route_utils import (
    best_insertion_delta,
    feasible_unvisited_nodes,
    greedy_closed_route,
    insert_node_best_position,
)


@dataclass(slots=True)
class NeighborMove:
    route: list[int]
    action: str
    node: int
    score: tuple[float, float]


def route_signature(route: Sequence[int]) -> tuple[int, ...]:
    return tuple(route)


def generate_neighbors(instance: OPInstance, route: Sequence[int]) -> list[NeighborMove]:
    neighbors: list[NeighborMove] = []
    visited_inner = list(route[1:-1])

    for node in feasible_unvisited_nodes(instance, route):
        candidate, delta = best_insertion_delta(instance, route, node)
        if candidate is not None:
            profit = instance.route_profit(candidate)
            cost = instance.route_cost(candidate)
            neighbors.append(NeighborMove(candidate, "insert", node, (profit, -cost)))

    for node in visited_inner:
        candidate = [route[0]] + [item for item in visited_inner if item != node] + [route[-1]]
        if candidate != list(route) and instance.validate_route(candidate) and instance.route_cost(candidate) <= instance.budget:
            profit = instance.route_profit(candidate)
            cost = instance.route_cost(candidate)
            neighbors.append(NeighborMove(candidate, "remove", node, (profit, -cost)))

    for index, node in enumerate(visited_inner):
        base = [route[0]] + [item for item in visited_inner if item != node] + [route[-1]]
        candidate = insert_node_best_position(instance, base, node)
        if candidate is not None and candidate != list(route):
            profit = instance.route_profit(candidate)
            cost = instance.route_cost(candidate)
            neighbors.append(NeighborMove(candidate, "relocate", node, (profit, -cost)))

    neighbors.sort(key=lambda item: (item.score[0], item.score[1], -len(item.route)), reverse=True)
    return neighbors


def initial_route(instance: OPInstance) -> list[int]:
    route, _, _ = greedy_closed_route(instance)
    return route
