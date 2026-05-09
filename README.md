# Orienteering Problem Solver

This repository contains an implementation framework for the Orienteering Problem.

## Current exact method
- Branch and Bound: `exact_approaches/branch_and_bound/`

## Shared benchmark instance
- `instances/shared_test/example_op.json`

## Run Branch and Bound
```bash
python -m exact_approaches.branch_and_bound.run --input instances/shared_test/example_op.json --output outputs/branch_and_bound/example_op_solution.json
```

The solver writes a JSON output that is ready for visualization or post-processing.
