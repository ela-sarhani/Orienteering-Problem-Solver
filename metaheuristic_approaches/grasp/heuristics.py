"""Helper functions for the GRASP approach."""

from __future__ import annotations

from math import ceil
from random import Random
from dataclasses import dataclass
from typing import Sequence

from exact_approaches.common.op_instance import OPInstance
from metaheuristic_approaches.common.route_utils import (
    best_insertion_delta,
    build_feasible_route_from_order,
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


def construct_route(instance: OPInstance, rng: Random, alpha: float) -> tuple[list[int], int]:
    route = [instance.start, instance.start]
    evaluations = 0

    while True:
        scored_candidates: list[tuple[float, int, list[int]]] = []
        for node in feasible_unvisited_nodes(instance, route):
            candidate, delta = best_insertion_delta(instance, route, node)
            evaluations += 1
            if candidate is None:
                continue
            profit = instance.profits[node]
            score = profit / delta if delta > 1e-12 else profit
            scored_candidates.append((score, node, candidate))

        if not scored_candidates:
            break

        scored_candidates.sort(key=lambda item: (item[0], -item[1]), reverse=True)
        rcl_size = max(1, ceil(alpha * len(scored_candidates)))
        chosen_score, chosen_node, chosen_route = rng.choice(scored_candidates[:rcl_size])
        if chosen_route == route:
            break
        route = chosen_route

    return route, evaluations


def local_neighbors(instance: OPInstance, route: Sequence[int]) -> list[NeighborMove]:
    neighbors: list[NeighborMove] = []
    visited_inner = list(route[1:-1])

    for node in feasible_unvisited_nodes(instance, route):
        candidate, _ = best_insertion_delta(instance, route, node)
        if candidate is not None:
            neighbors.append(NeighborMove(candidate, "insert", node, (instance.route_profit(candidate), -instance.route_cost(candidate))))

    for node in visited_inner:
        candidate = [route[0]] + [item for item in visited_inner if item != node] + [route[-1]]
        if candidate != list(route) and instance.validate_route(candidate) and instance.route_cost(candidate) <= instance.budget:
            neighbors.append(NeighborMove(candidate, "remove", node, (instance.route_profit(candidate), -instance.route_cost(candidate))))

    for node in visited_inner:
        base = [route[0]] + [item for item in visited_inner if item != node] + [route[-1]]
        candidate = insert_node_best_position(instance, base, node)
        if candidate is not None and candidate != list(route):
            neighbors.append(NeighborMove(candidate, "relocate", node, (instance.route_profit(candidate), -instance.route_cost(candidate))))

    neighbors.sort(key=lambda item: (item.score[0], item.score[1]), reverse=True)
    return neighbors


def local_search(instance: OPInstance, route: Sequence[int]) -> tuple[list[int], int]:
    current_route = list(route)
    evaluations = 0

    improved = True
    while improved:
        improved = False
        neighbors = local_neighbors(instance, current_route)
        evaluations += len(neighbors)
        for move in neighbors:
            if instance.route_profit(move.route) > instance.route_profit(current_route):
                current_route = list(move.route)
                improved = True
                break

    return current_route, evaluations
