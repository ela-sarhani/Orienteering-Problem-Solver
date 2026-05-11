"""Command-line runner for the Genetic Algorithm approach."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from exact_approaches.common.op_instance import OPInstance
from .solver import GeneticAlgorithmSolver
from .visualization.viewer import generate_html_viewer


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Solve an Orienteering Problem instance with a Genetic Algorithm.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("instances/shared_test/example_op.json"),
        help="Path to the structured OP instance JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/metaheuristics/genetic_algorithm/example_op_solution.json"),
        help="Path where the solution JSON will be written.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    instance = OPInstance.from_json(args.input)
    solver = GeneticAlgorithmSolver()
    solution = solver.solve(instance)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    solution_dict = solution.to_dict(instance)
    args.output.write_text(json.dumps(solution_dict, indent=2), encoding="utf-8")

    html_output = args.output.parent / f"{args.output.stem}_viewer.html"
    generate_html_viewer(
        instance_data={
            "name": instance.name,
            "n": instance.n,
            "budget": instance.budget,
            "cost_matrix": instance.cost_matrix,
            "visualization": solution_dict.get("visualization", {}),
            "best_route": solution.route,
            "best_profit": solution.total_profit,
            "best_cost": solution.total_cost,
        },
        algorithm_steps=solution.metadata.get("state_history", {}),
        output_path=html_output,
    )

    print(f"Instance: {instance.name}")
    print(f"Best profit: {solution.total_profit:.6f}")
    print(f"Route cost: {solution.total_cost:.6f}")
    print(f"Route: {solution.route}")
    print(f"Output written to: {args.output}")
    print(f"Viewer written to: {html_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
