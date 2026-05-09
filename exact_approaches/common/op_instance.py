"""
OP Instance Data Model.
Responsible for:
- Parsing JSON instance files (coordinates, profits, budget, start vertex).
- Computing distance matrices (Euclidean or from explicit cost matrix).
- Providing helper methods to compute route cost, profit, and visualization data.
Used by all exact and heuristic methods as the canonical problem representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Any, Sequence


@dataclass(slots=True)
class OPInstance:
    name: str
    start: int
    coords: list[tuple[float, float] | None]
    profits: list[float]
    budget: float
    cost_matrix: list[list[float]]
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: str | Path) -> "OPInstance":
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))

        name = str(raw.get("name", path.stem))
        start = int(raw.get("start", 0))

        coords_raw = raw.get("coords")
        cost_matrix_raw = raw.get("cost_matrix")
        profits_raw = raw.get("profits")
        n_raw = raw.get("n")

        coords: list[tuple[float, float] | None]
        cost_matrix: list[list[float]]

        if coords_raw is not None:
            coords = [tuple(map(float, pair)) for pair in coords_raw]
            n = len(coords)
        elif cost_matrix_raw is not None:
            n = len(cost_matrix_raw)
            coords = [None] * n
        elif n_raw is not None:
            n = int(n_raw)
            coords = [None] * n
        else:
            raise ValueError("The instance JSON must define at least 'coords', 'cost_matrix', or 'n'.")

        if profits_raw is None:
            raise ValueError("The instance JSON must define 'profits'.")
        profits = [float(value) for value in profits_raw]
        if len(profits) != n:
            raise ValueError(f"Expected {n} profits, received {len(profits)}.")

        if cost_matrix_raw is not None:
            cost_matrix = [[float(value) for value in row] for row in cost_matrix_raw]
            if len(cost_matrix) != n or any(len(row) != n for row in cost_matrix):
                raise ValueError("The cost matrix must be square with size n x n.")
        elif coords_raw is not None:
            cost_matrix = cls._euclidean_cost_matrix(coords)
        else:
            raise ValueError("The instance JSON must define either 'coords' or 'cost_matrix'.")

        if not 0 <= start < n:
            raise ValueError(f"Start vertex {start} is outside the valid range 0..{n - 1}.")

        metadata = {
            key: value
            for key, value in raw.items()
            if key not in {"name", "start", "coords", "cost_matrix", "profits", "n", "budget"}
        }

        budget = float(raw.get("budget", 0.0))
        if budget <= 0:
            raise ValueError("The instance JSON must define a strictly positive 'budget'.")

        return cls(
            name=name,
            start=start,
            coords=coords,
            profits=profits,
            budget=budget,
            cost_matrix=cost_matrix,
            metadata=metadata,
        )

    @staticmethod
    def _euclidean_cost_matrix(coords: Sequence[tuple[float, float] | None]) -> list[list[float]]:
        numeric_coords: list[tuple[float, float]] = []
        for index, coord in enumerate(coords):
            if coord is None:
                raise ValueError(f"Coordinate at index {index} is missing.")
            numeric_coords.append((float(coord[0]), float(coord[1])))

        n = len(numeric_coords)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            x_i, y_i = numeric_coords[i]
            for j in range(i + 1, n):
                x_j, y_j = numeric_coords[j]
                distance = math.hypot(x_i - x_j, y_i - y_j)
                matrix[i][j] = distance
                matrix[j][i] = distance
        return matrix

    @property
    def n(self) -> int:
        return len(self.profits)

    @property
    def has_coordinates(self) -> bool:
        return all(coord is not None for coord in self.coords)

    def distance(self, i: int, j: int) -> float:
        return self.cost_matrix[i][j]

    def route_cost(self, route: Sequence[int]) -> float:
        return sum(self.distance(route[index], route[index + 1]) for index in range(len(route) - 1))

    def route_profit(self, route: Sequence[int]) -> float:
        return sum(self.profits[node] for node in route[1:-1])

    def route_edges(self, route: Sequence[int]) -> list[list[int]]:
        return [[route[index], route[index + 1]] for index in range(len(route) - 1)]

    def validate_route(self, route: Sequence[int]) -> bool:
        if len(route) < 2:
            return False
        if route[0] != self.start or route[-1] != self.start:
            return False
        inner_nodes = route[1:-1]
        if self.start in inner_nodes:
            return False
        if len(inner_nodes) != len(set(inner_nodes)):
            return False
        return all(0 <= node < self.n for node in route)

    def route_points(self, route: Sequence[int]) -> list[list[float]]:
        if not self.has_coordinates:
            return []
        points: list[list[float]] = []
        for node in route:
            coord = self.coords[node]
            if coord is None:
                return []
            points.append([coord[0], coord[1]])
        return points

    def visualisation_payload(self, route: Sequence[int]) -> dict[str, Any]:
        visited_nodes = set(route[1:-1])
        nodes: list[dict[str, Any]] = []
        for node_id in range(self.n):
            entry: dict[str, Any] = {
                "id": node_id,
                "profit": self.profits[node_id],
                "visited": node_id in visited_nodes,
            }
            coord = self.coords[node_id]
            if coord is not None:
                entry["x"] = coord[0]
                entry["y"] = coord[1]
            nodes.append(entry)

        return {
            "name": self.name,
            "start": self.start,
            "budget": self.budget,
            "route": list(route),
            "route_edges": self.route_edges(route),
            "route_points": self.route_points(route),
            "nodes": nodes,
            "route_cost": self.route_cost(route),
            "route_profit": self.route_profit(route),
            "has_coordinates": self.has_coordinates,
        }
