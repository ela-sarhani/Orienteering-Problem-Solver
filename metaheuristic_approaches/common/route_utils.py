"""Route helpers shared by the metaheuristic approaches."""

from __future__ import annotations

from random import Random
from typing import Sequence

from exact_approaches.common.op_instance import OPInstance


def route_cost(instance: OPInstance, route: Sequence[int]) -> float:
    return instance.route_cost(route)


def route_profit(instance: OPInstance, route: Sequence[int]) -> float:
    return instance.route_profit(route)


def insert_node_best_position(instance: OPInstance, route: Sequence[int], node: int) -> list[int] | None:
    if node == instance.start:
        return None

    if node in route:
        return None

    best_route: list[int] | None = None
    best_cost = float("inf")

    for index in range(1, len(route)):
        candidate = list(route[:index]) + [node] + list(route[index:])
        if not instance.validate_route(candidate):
            continue
        candidate_cost = instance.route_cost(candidate)
        if candidate_cost <= instance.budget and candidate_cost < best_cost:
            best_cost = candidate_cost
            best_route = candidate

    return best_route


def best_insertion_delta(instance: OPInstance, route: Sequence[int], node: int) -> tuple[list[int] | None, float]:
    best_route = insert_node_best_position(instance, route, node)
    if best_route is None:
        return None, float("inf")
    return best_route, instance.route_cost(best_route) - instance.route_cost(route)


def feasible_unvisited_nodes(instance: OPInstance, route: Sequence[int]) -> list[int]:
    visited = set(route)
    return [node for node in range(instance.n) if node != instance.start and node not in visited]


def build_feasible_route_from_order(instance: OPInstance, node_order: Sequence[int]) -> list[int]:
    route = [instance.start, instance.start]
    for node in node_order:
        if node == instance.start or node in route:
            continue
        candidate = insert_node_best_position(instance, route, node)
        if candidate is not None:
            route = candidate
    return route


def greedy_closed_route(instance: OPInstance) -> tuple[list[int], float, float]:
    remaining = [node for node in range(instance.n) if node != instance.start]
    remaining.sort(key=lambda node: (-instance.profits[node], instance.distance(instance.start, node), node))
    route = build_feasible_route_from_order(instance, remaining)
    return route, instance.route_profit(route), instance.route_cost(route)


def random_feasible_route(instance: OPInstance, rng: Random) -> list[int]:
    nodes = [node for node in range(instance.n) if node != instance.start]
    rng.shuffle(nodes)
    return build_feasible_route_from_order(instance, nodes)
