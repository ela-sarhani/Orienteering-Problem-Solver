"""
Greedy Heuristic for B&B.
Builds an initial feasible route by greedily adding high-profit nodes.
Used to obtain a starting incumbent solution for B&B pruning.
Optional but improves performance by enabling early pruning.
"""

from __future__ import annotations

from exact_approaches.common.op_instance import OPInstance


def greedy_closed_route(instance: OPInstance) -> tuple[list[int], float, float]:
    """Build a quick feasible route by repeatedly appending the best profitable node.

    The route always remains closable within the budget after each append.
    """

    start = instance.start
    route = [start]
    current = start
    open_cost = 0.0
    remaining = set(range(instance.n)) - {start}
    eps = 1e-12

    while remaining:
        best_node = None
        best_key = None
        current_to_start = instance.distance(current, start)

        for node in remaining:
            additional_closed_cost = (
                open_cost
                + instance.distance(current, node)
                + instance.distance(node, start)
                - (open_cost + current_to_start)
            )
            closes_now_cost = open_cost + instance.distance(current, node) + instance.distance(node, start)
            if closes_now_cost > instance.budget + eps:
                continue

            profit = instance.profits[node]
            if additional_closed_cost <= eps:
                key = (1, profit, -additional_closed_cost, -node)
            else:
                key = (0, profit / additional_closed_cost, profit, -additional_closed_cost, -node)

            if best_key is None or key > best_key:
                best_key = key
                best_node = node

        if best_node is None:
            break

        route.append(best_node)
        open_cost += instance.distance(current, best_node)
        current = best_node
        remaining.remove(best_node)

    route.append(start)
    total_cost = instance.route_cost(route)
    total_profit = instance.route_profit(route)
    return route, total_profit, total_cost
