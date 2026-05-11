# Orienteering Problem Solver

This repository implements exact and metaheuristic approaches for the Orienteering Problem, with JSON outputs and interactive HTML visualizations for every run.

## Project Layout

- `exact_approaches/` contains Branch and Bound, Branch and Cut, and Dynamic Programming.
- `metaheuristic_approaches/` contains Genetic Algorithm, Tabu Search, and GRASP.
- `instances/` contains the benchmark instance used for validation plus two comparison instances.
- `outputs/` stores solution JSON files, HTML viewers, and comparative experiment reports.

## Requirements

The project uses the Python standard library only. No third-party Python packages are required in `requirements.txt`.

Use the workspace virtual environment located at `c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe`.

## Run the Exact Solvers

Run each solver on the shared benchmark instance:

```powershell
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m exact_approaches.branch_and_bound.run --input instances/shared_test/example_op.json --output outputs/branch_and_bound/example_op_solution.json
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m exact_approaches.branch_and_cut.run --input instances/shared_test/example_op.json --output outputs/branch_and_cut/example_op_solution.json
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m exact_approaches.dynamic_programming.run --input instances/shared_test/example_op.json --output outputs/dynamic_programming/example_op_solution.json
```

Each command writes a solution JSON file and a companion HTML viewer in the same output folder.

## Run the Metaheuristics

Run the three heuristic approaches on the same benchmark instance:

```powershell
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m metaheuristic_approaches.genetic_algorithm.run --input instances/shared_test/example_op.json --output outputs/metaheuristics/genetic_algorithm/example_op_solution.json
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m metaheuristic_approaches.tabu_search.run --input instances/shared_test/example_op.json --output outputs/metaheuristics/tabu_search/example_op_solution.json
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" -m metaheuristic_approaches.grasp.run --input instances/shared_test/example_op.json --output outputs/metaheuristics/grasp/example_op_solution.json
```

These commands also generate HTML viewers next to the solution files.

## Run the Full Comparative Study

The comparative experiment runner executes all six approaches on three instances:

- `instances/shared_test/example_op.json`
- `instances/comparative/medium_op.json`
- `instances/comparative/large_op.json`

Run the complete study with:

```powershell
& "c:/Users/ela/Desktop/ICE3/Optimisation Combinatoire/.venv/bin/python.exe" run_comparative_experiments.py
```

This writes per-run solution files and viewers under `outputs/comparative_experiments/<instance>/<method>/`.

## View the Results

Open the following files after the comparative run:

- `outputs/comparative_experiments/comparative_results.md` for the documented KPI summary.
- `outputs/comparative_experiments/comparative_results.json` for the structured results.
- Any `*_viewer.html` file under `outputs/` to replay a solver step-by-step in the browser.

## Included KPIs

The comparative report includes:

- total profit
- route cost
- feasibility
- runtime
- route length
- nodes explored or iterations
- pruned units
- recorded visualization steps
- candidate evaluations
- gap to the best observed profit on each instance

## Notes

- The exact methods are intended as baselines and optimality references for the smaller instances.
- The metaheuristics use the same solution container and visualization style, so their outputs can be compared directly.
- The scientific report is intentionally left out of this implementation pass.
