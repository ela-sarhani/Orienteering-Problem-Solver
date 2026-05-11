"""Helper functions for the Genetic Algorithm approach."""

from __future__ import annotations

from random import Random
from typing import Sequence

from exact_approaches.common.op_instance import OPInstance
from metaheuristic_approaches.common.route_utils import (
    build_feasible_route_from_order,
    feasible_unvisited_nodes,
    greedy_closed_route,
    route_cost,
    route_profit,
)


def route_to_genome(instance: OPInstance, route: Sequence[int]) -> list[int]:
    return [node for node in route[1:-1] if node != instance.start]


def genome_to_route(instance: OPInstance, genome: Sequence[int]) -> list[int]:
    return build_feasible_route_from_order(instance, genome)


def fitness(instance: OPInstance, route: Sequence[int]) -> float:
    cost = route_cost(instance, route)
    profit = route_profit(instance, route)
    if cost <= instance.budget:
        return profit
    return profit - 1000.0 * (cost - instance.budget)


def random_genome(instance: OPInstance, rng: Random) -> list[int]:
    nodes = feasible_unvisited_nodes(instance, [instance.start, instance.start])
    rng.shuffle(nodes)
    return nodes


def initialize_population(instance: OPInstance, rng: Random, population_size: int) -> list[list[int]]:
    population: list[list[int]] = []
    greedy_route, _, _ = greedy_closed_route(instance)
    population.append(route_to_genome(instance, greedy_route))

    while len(population) < population_size:
        genome = random_genome(instance, rng)
        route = genome_to_route(instance, genome)
        if route not in ([instance.start, instance.start]):
            population.append(route_to_genome(instance, route))
    return population


def tournament_select(population: Sequence[list[int]], scores: Sequence[float], rng: Random, tournament_size: int = 3) -> list[int]:
    candidates = rng.sample(range(len(population)), k=min(tournament_size, len(population)))
    best_index = max(candidates, key=lambda index: scores[index])
    return list(population[best_index])


def ordered_crossover(parent_a: Sequence[int], parent_b: Sequence[int], rng: Random) -> list[int]:
    if not parent_a:
        return list(parent_b)
    if not parent_b:
        return list(parent_a)

    size = min(len(parent_a), len(parent_b))
    if size < 2:
        return list(parent_a if rng.random() < 0.5 else parent_b)

    left = rng.randint(0, size - 2)
    right = rng.randint(left + 1, size - 1)
    child = [-1] * size
    child[left:right] = parent_a[left:right]

    fill_values = [node for node in parent_b if node not in child]
    fill_index = 0
    for index in range(size):
        if child[index] == -1:
            child[index] = fill_values[fill_index]
            fill_index += 1
    return child


def mutate_genome(genome: list[int], rng: Random, mutation_rate: float) -> list[int]:
    mutated = list(genome)
    if len(mutated) >= 2 and rng.random() < mutation_rate:
        i, j = rng.sample(range(len(mutated)), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
    elif mutated and rng.random() < mutation_rate:
        i = rng.randrange(len(mutated))
        node = mutated.pop(i)
        j = rng.randrange(len(mutated) + 1)
        mutated.insert(j, node)
    return mutated
