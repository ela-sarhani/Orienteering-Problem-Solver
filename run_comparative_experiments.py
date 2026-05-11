"""Run the full comparative experiment suite for the Orienteering Problem project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import time
from statistics import mean
from typing import Any, Callable

from exact_approaches.branch_and_bound import BranchAndBoundSolver
from exact_approaches.branch_and_bound.visualization.viewer import generate_html_viewer as bb_viewer
from exact_approaches.branch_and_cut import BranchAndCutSolver
from exact_approaches.branch_and_cut.visualization.viewer import generate_html_viewer as bc_viewer
from exact_approaches.common.op_instance import OPInstance
from exact_approaches.dynamic_programming import DynamicProgrammingSolver
from exact_approaches.dynamic_programming.visualization.viewer import generate_html_viewer as dp_viewer
from metaheuristic_approaches.genetic_algorithm import GeneticAlgorithmSolver
from metaheuristic_approaches.genetic_algorithm.visualization.viewer import generate_html_viewer as ga_viewer
from metaheuristic_approaches.grasp import GraspSolver
from metaheuristic_approaches.grasp.visualization.viewer import generate_html_viewer as grasp_viewer
from metaheuristic_approaches.tabu_search import TabuSearchSolver
from metaheuristic_approaches.tabu_search.visualization.viewer import generate_html_viewer as tabu_viewer
from viewer_hub import generate_viewer_hub


@dataclass(slots=True)
class MethodSpec:
    name: str
    factory: Callable[[], Any]
    viewer: Callable[[dict[str, Any], dict[str, Any], str | Path], None]
    output_folder: str


METHODS: list[MethodSpec] = [
    MethodSpec("branch_and_bound", BranchAndBoundSolver, bb_viewer, "branch_and_bound"),
    MethodSpec("branch_and_cut", BranchAndCutSolver, bc_viewer, "branch_and_cut"),
    MethodSpec("dynamic_programming", DynamicProgrammingSolver, dp_viewer, "dynamic_programming"),
    MethodSpec("genetic_algorithm", GeneticAlgorithmSolver, ga_viewer, "genetic_algorithm"),
    MethodSpec("tabu_search", TabuSearchSolver, tabu_viewer, "tabu_search"),
    MethodSpec("grasp", GraspSolver, grasp_viewer, "grasp"),
]

INSTANCE_PATHS = [
    Path("instances/shared_test/example_op.json"),
    Path("instances/comparative/medium_op.json"),
    Path("instances/comparative/large_op.json"),
]


def _write_solution_assets(output_root: Path, instance: OPInstance, spec: MethodSpec, solution) -> dict[str, Any]:
    instance_folder = output_root / instance.name / spec.output_folder
    instance_folder.mkdir(parents=True, exist_ok=True)

    solution_path = instance_folder / f"{instance.name}_{spec.name}_solution.json"
    solution_dict = solution.to_dict(instance)
    solution_path.write_text(json.dumps(solution_dict, indent=2), encoding="utf-8")

    html_path = instance_folder / f"{instance.name}_{spec.name}_viewer.html"
    spec.viewer(
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
        output_path=html_path,
    )

    history = solution.metadata.get("state_history", {}) or {}
    last_step = history.get("steps", [{}])[-1] if history.get("steps") else {}

    return {
        "instance": instance.name,
        "method": spec.name,
        "route": solution.route,
        "profit": solution.total_profit,
        "cost": solution.total_cost,
        "feasible": solution.feasible,
        "runtime_seconds": solution.runtime_seconds,
        "route_length": max(0, len(solution.route) - 2),
        "search_units": solution.nodes_explored,
        "pruned_units": solution.pruned_nodes,
        "state_steps": history.get("total_steps", 0),
        "candidate_evaluations": last_step.get("candidate_evaluations", 0),
        "solution_path": str(solution_path),
        "viewer_path": str(html_path),
        "metadata": solution.metadata,
    }


def _format_row(values: list[str], widths: list[int]) -> str:
    return "| " + " | ".join(value.ljust(widths[index]) for index, value in enumerate(values)) + " |"


def _build_markdown_report(records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Comparative Experiments Report")
    lines.append("")
    lines.append("This file summarizes the comparative study across the six implemented approaches on three Orienteering Problem instances.")
    lines.append("")
    lines.append("## Instances")
    lines.append("")
    lines.append("- `shared_test_example_op` - the benchmark used for the exact-solver validation.")
    lines.append("- `comparative_medium_op` - a slightly larger instance added for the comparison study.")
    lines.append("- `comparative_large_op` - the largest instance in this report, still sized to keep exact methods tractable.")
    lines.append("")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record["instance"], []).append(record)

    method_width = max(len("Method"), max(len(record["method"]) for record in records))
    route_width = max(len("Route"), max(len(str(record["route"])) for record in records))
    profit_width = len("Profit")
    cost_width = len("Cost")
    feasible_width = len("Feasible")
    runtime_width = len("Runtime (s)")
    route_len_width = len("Route Len")
    search_width = len("Search Units")
    pruned_width = len("Pruned")
    steps_width = len("State Steps")
    eval_width = len("Candidate Evals")
    gap_width = len("Gap to Best")

    for instance_name, instance_records in grouped.items():
        best_profit = max(record["profit"] for record in instance_records)
        best_record = max(instance_records, key=lambda record: (record["profit"], -record["runtime_seconds"]))

        lines.append(f"## {instance_name}")
        lines.append("")
        lines.append(f"Best observed profit: **{best_profit:.2f}**")
        lines.append(f"Best route: **{best_record['route']}**")
        lines.append("")
        lines.append(_format_row(
            ["Method", "Profit", "Cost", "Feasible", "Runtime (s)", "Route Len", "Search Units", "Pruned", "State Steps", "Candidate Evals", "Gap to Best", "Route"],
            [method_width, profit_width, cost_width, feasible_width, runtime_width, route_len_width, search_width, pruned_width, steps_width, eval_width, gap_width, route_width],
        ))
        lines.append(_format_row(
            ["---"] * 12,
            [method_width, profit_width, cost_width, feasible_width, runtime_width, route_len_width, search_width, pruned_width, steps_width, eval_width, gap_width, route_width],
        ))
        for record in sorted(instance_records, key=lambda record: record["method"]):
            gap = best_profit - record["profit"]
            lines.append(_format_row(
                [
                    record["method"],
                    f"{record['profit']:.2f}",
                    f"{record['cost']:.2f}",
                    "yes" if record["feasible"] else "no",
                    f"{record['runtime_seconds']:.4f}",
                    str(record["route_length"]),
                    str(record["search_units"]),
                    str(record["pruned_units"]),
                    str(record["state_steps"]),
                    str(record["candidate_evaluations"]),
                    f"{gap:.2f}",
                    str(record["route"]),
                ],
                [method_width, profit_width, cost_width, feasible_width, runtime_width, route_len_width, search_width, pruned_width, steps_width, eval_width, gap_width, route_width],
            ))
        lines.append("")

    lines.append("## Aggregate Averages")
    lines.append("")
    lines.append(_format_row(["Method", "Mean Profit", "Mean Runtime (s)", "Mean Gap"], [method_width, len("Mean Profit"), len("Mean Runtime (s)"), len("Mean Gap")]))
    lines.append(_format_row(["---", "---", "---", "---"], [method_width, len("Mean Profit"), len("Mean Runtime (s)"), len("Mean Gap")]))
    for method in sorted({record["method"] for record in records}):
        method_records = [record for record in records if record["method"] == method]
        mean_profit = mean(record["profit"] for record in method_records)
        mean_runtime = mean(record["runtime_seconds"] for record in method_records)
        mean_gap = mean(max(record["profit"] for record in grouped[record["instance"]]) - record["profit"] for record in method_records)
        lines.append(_format_row([method, f"{mean_profit:.2f}", f"{mean_runtime:.4f}", f"{mean_gap:.2f}"], [method_width, len("Mean Profit"), len("Mean Runtime (s)"), len("Mean Gap")]))

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `Search Units` corresponds to nodes explored for exact methods and iterations for the metaheuristics.")
    lines.append("- `State Steps` is the number of recorded visualization states written into each solution metadata block.")
    lines.append("- All artifacts for each run are stored under `outputs/comparative_experiments/<instance>/<method>/`.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    output_root = Path("outputs/comparative_experiments")
    output_root.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    run_manifest: list[dict[str, Any]] = []

    for instance_path in INSTANCE_PATHS:
        instance = OPInstance.from_json(instance_path)
        for spec in METHODS:
            start_time = time.perf_counter()
            solver = spec.factory()
            solution = solver.solve(instance)
            elapsed = time.perf_counter() - start_time

            record = _write_solution_assets(output_root, instance, spec, solution)
            record["wall_clock_seconds"] = elapsed
            records.append(record)
            run_manifest.append(
                {
                    "instance": instance.name,
                    "method": spec.name,
                    "solution_path": record["solution_path"],
                    "viewer_path": record["viewer_path"],
                }
            )
            print(f"{instance.name} / {spec.name}: profit={record['profit']:.2f}, cost={record['cost']:.2f}, runtime={record['runtime_seconds']:.4f}s")

    report_md = _build_markdown_report(records)
    report_path = output_root / "comparative_results.md"
    report_path.write_text(report_md, encoding="utf-8")

    summary_path = output_root / "comparative_results.json"
    summary_path.write_text(
        json.dumps(
            {
                "instances": [str(path) for path in INSTANCE_PATHS],
                "records": records,
                "runs": run_manifest,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    generate_viewer_hub(
        output_root.parent / "index.html",
        exact_viewers=[
            ("Branch and Bound", "comparative_experiments/shared_test_example_op/branch_and_bound/shared_test_example_op_branch_and_bound_viewer.html"),
            ("Branch and Cut", "comparative_experiments/shared_test_example_op/branch_and_cut/shared_test_example_op_branch_and_cut_viewer.html"),
            ("Dynamic Programming", "comparative_experiments/shared_test_example_op/dynamic_programming/shared_test_example_op_dynamic_programming_viewer.html"),
        ],
        metaheuristic_viewers=[
            ("Genetic Algorithm", "comparative_experiments/shared_test_example_op/genetic_algorithm/shared_test_example_op_genetic_algorithm_viewer.html"),
            ("Tabu Search", "comparative_experiments/shared_test_example_op/tabu_search/shared_test_example_op_tabu_search_viewer.html"),
            ("GRASP", "comparative_experiments/shared_test_example_op/grasp/shared_test_example_op_grasp_viewer.html"),
        ],
    )

    print(f"Comparative report written to: {report_path}")
    print(f"Comparative JSON written to: {summary_path}")
    print(f"Viewer hub written to: {output_root.parent / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
