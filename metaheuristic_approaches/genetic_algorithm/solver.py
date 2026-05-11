"""Genetic Algorithm solver for the Orienteering Problem."""

from __future__ import annotations

from dataclasses import dataclass
import random
import time

from exact_approaches.common.op_instance import OPInstance
from exact_approaches.common.solution import OPSolution
from metaheuristic_approaches.common.route_utils import greedy_closed_route
from metaheuristic_approaches.common.state_recorder import StateRecorder

from .heuristics import (
    fitness,
    genome_to_route,
    initialize_population,
    mutate_genome,
    ordered_crossover,
    route_to_genome,
    tournament_select,
)


@dataclass(slots=True)
class GeneticAlgorithmConfig:
    population_size: int = 28
    generations: int = 80
    mutation_rate: float = 0.22
    crossover_rate: float = 0.85
    elite_count: int = 2
    seed: int = 7


class GeneticAlgorithmSolver:
    def __init__(self, config: GeneticAlgorithmConfig | None = None) -> None:
        self.config = config or GeneticAlgorithmConfig()
        self._recorder = StateRecorder(enable_recording=True)

    def solve(self, instance: OPInstance) -> OPSolution:
        rng = random.Random(self.config.seed)
        self._recorder = StateRecorder(enable_recording=True)
        start_time = time.perf_counter()

        greedy_route, greedy_profit, greedy_cost = greedy_closed_route(instance)
        best_route = list(greedy_route)
        best_profit = greedy_profit
        best_cost = greedy_cost
        best_source = "greedy"

        population = initialize_population(instance, rng, self.config.population_size)
        population = [route_to_genome(instance, genome_to_route(instance, genome)) for genome in population]

        candidate_evaluations = 0
        self._recorder.record_step(
            action="initialize",
            route=best_route,
            current_profit=best_profit,
            current_cost=best_cost,
            remaining_budget=instance.budget - best_cost,
            iterations=0,
            candidate_evaluations=candidate_evaluations,
            decision_reason="greedy incumbent initialized",
            best_incumbent_profit=best_profit,
        )

        for generation in range(1, self.config.generations + 1):
            scored_population: list[tuple[float, list[int]]] = []
            for genome in population:
                route = genome_to_route(instance, genome)
                score = fitness(instance, route)
                scored_population.append((score, list(genome)))
                candidate_evaluations += 1

                profit = instance.route_profit(route)
                cost = instance.route_cost(route)
                if cost <= instance.budget and profit > best_profit:
                    best_route = list(route)
                    best_profit = profit
                    best_cost = cost
                    best_source = f"generation_{generation}"
                    self._recorder.record_step(
                        action="update_incumbent",
                        route=best_route,
                        current_profit=best_profit,
                        current_cost=best_cost,
                        remaining_budget=instance.budget - best_cost,
                        iterations=generation,
                        candidate_evaluations=candidate_evaluations,
                        decision_reason=f"new best route found in generation {generation}",
                        best_incumbent_profit=best_profit,
                    )

            scored_population.sort(key=lambda item: item[0], reverse=True)
            ordered_population = [list(genome) for _, genome in scored_population]
            ordered_scores = [score for score, _ in scored_population]
            elites = ordered_population[: self.config.elite_count]

            next_population = list(elites)
            while len(next_population) < self.config.population_size:
                parent_a = tournament_select(ordered_population, ordered_scores, rng)
                parent_b = tournament_select(ordered_population, ordered_scores, rng)
                child = list(parent_a)
                if rng.random() < self.config.crossover_rate:
                    child = ordered_crossover(parent_a, parent_b, rng)
                child = mutate_genome(child, rng, self.config.mutation_rate)
                next_population.append(child)

            population = next_population
            self._recorder.record_step(
                action="generation",
                route=best_route,
                current_profit=best_profit,
                current_cost=best_cost,
                remaining_budget=instance.budget - best_cost,
                iterations=generation,
                candidate_evaluations=candidate_evaluations,
                decision_reason=f"completed generation {generation}; best source={best_source}",
                best_incumbent_profit=best_profit,
            )

        runtime = time.perf_counter() - start_time
        solution = OPSolution(
            route=best_route,
            total_profit=best_profit,
            total_cost=best_cost,
            feasible=best_cost <= instance.budget,
            method="genetic_algorithm",
            nodes_explored=self.config.generations,
            pruned_nodes=max(0, candidate_evaluations - len(population)),
            runtime_seconds=runtime,
            metadata={
                "algorithm": "genetic_algorithm",
                "state_history": self._recorder.to_dict(),
                "best_source": best_source,
            },
        )
        return solution
