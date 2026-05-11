# Comparative Experiments Report

This file summarizes the comparative study across the six implemented approaches on three Orienteering Problem instances.

## Instances

- `shared_test_example_op` - the benchmark used for the exact-solver validation.
- `comparative_medium_op` - a slightly larger instance added for the comparison study.
- `comparative_large_op` - the largest instance in this report, still sized to keep exact methods tractable.

## shared_test_example_op

Best observed profit: **22.00**
Best route: **[0, 1, 2, 4, 0]**

| Method              | Profit | Cost | Feasible | Runtime (s) | Route Len | Search Units | Pruned | State Steps | Candidate Evals | Gap to Best | Route                    |
| ---                 | ---    | ---  | ---      | ---         | ---       | ---          | ---    | ---         | ---             | ---         | ---                      |
| branch_and_bound    | 22.00  | 13.19 | yes      | 0.0053      | 3         | 252          | 422    | 674         | 0               | 0.00        | [0, 2, 4, 1, 0]          |
| branch_and_cut      | 22.00  | 13.63 | yes      | 0.0014      | 3         | 69           | 54     | 122         | 0               | 0.00        | [0, 1, 2, 4, 0]          |
| dynamic_programming | 22.00  | 13.63 | yes      | 0.0067      | 3         | 252          | 422    | 674         | 0               | 0.00        | [0, 1, 2, 4, 0]          |
| genetic_algorithm   | 22.00  | 13.19 | yes      | 0.1406      | 3         | 80           | 2212   | 84          | 2240            | 0.00        | [0, 2, 4, 1, 0]          |
| grasp               | 22.00  | 13.19 | yes      | 0.0327      | 3         | 70           | 1400   | 72          | 1470            | 0.00        | [0, 2, 4, 1, 0]          |
| tabu_search         | 22.00  | 13.19 | yes      | 0.0137      | 3         | 90           | 183    | 91          | 273             | 0.00        | [0, 2, 4, 1, 0]          |

## comparative_medium_op

Best observed profit: **37.00**
Best route: **[0, 3, 5, 6, 4, 1, 0]**

| Method              | Profit | Cost | Feasible | Runtime (s) | Route Len | Search Units | Pruned | State Steps | Candidate Evals | Gap to Best | Route                    |
| ---                 | ---    | ---  | ---      | ---         | ---       | ---          | ---    | ---         | ---             | ---         | ---                      |
| branch_and_bound    | 37.00  | 17.88 | yes      | 0.0230      | 5         | 1194         | 2176   | 3371        | 0               | 0.00        | [0, 3, 5, 6, 4, 1, 0]    |
| branch_and_cut      | 33.00  | 17.60 | yes      | 0.0039      | 4         | 192          | 154    | 345         | 0               | 4.00        | [0, 1, 2, 4, 7, 0]       |
| dynamic_programming | 33.00  | 17.60 | yes      | 0.0328      | 4         | 1191         | 2167   | 3355        | 0               | 4.00        | [0, 1, 2, 4, 7, 0]       |
| genetic_algorithm   | 37.00  | 17.88 | yes      | 0.2999      | 5         | 80           | 2212   | 82          | 2240            | 0.00        | [0, 3, 5, 6, 4, 1, 0]    |
| grasp               | 37.00  | 17.88 | yes      | 0.0622      | 5         | 70           | 2060   | 74          | 2130            | 0.00        | [0, 3, 5, 6, 4, 1, 0]    |
| tabu_search         | 37.00  | 17.88 | yes      | 0.0295      | 5         | 90           | 392    | 91          | 482             | 0.00        | [0, 1, 4, 6, 5, 3, 0]    |

## comparative_large_op

Best observed profit: **51.00**
Best route: **[0, 2, 4, 7, 6, 5, 3, 0]**

| Method              | Profit | Cost | Feasible | Runtime (s) | Route Len | Search Units | Pruned | State Steps | Candidate Evals | Gap to Best | Route                    |
| ---                 | ---    | ---  | ---      | ---         | ---       | ---          | ---    | ---         | ---             | ---         | ---                      |
| branch_and_bound    | 51.00  | 19.66 | yes      | 0.1037      | 6         | 3883         | 8991   | 12879       | 0               | 0.00        | [0, 2, 4, 7, 6, 5, 3, 0] |
| branch_and_cut      | 49.00  | 19.60 | yes      | 0.0127      | 6         | 546          | 451    | 1000        | 0               | 2.00        | [0, 1, 2, 4, 7, 6, 5, 0] |
| dynamic_programming | 34.00  | 17.60 | yes      | 0.1278      | 4         | 3863         | 8854   | 12684       | 0               | 17.00       | [0, 1, 2, 4, 8, 0]       |
| genetic_algorithm   | 51.00  | 19.66 | yes      | 0.4663      | 6         | 80           | 2212   | 82          | 2240            | 0.00        | [0, 2, 4, 7, 6, 5, 3, 0] |
| grasp               | 51.00  | 19.66 | yes      | 0.1119      | 6         | 70           | 2719   | 73          | 2789            | 0.00        | [0, 2, 4, 7, 6, 5, 3, 0] |
| tabu_search         | 51.00  | 19.66 | yes      | 0.0401      | 6         | 90           | 492    | 92          | 582             | 0.00        | [0, 2, 4, 7, 6, 5, 3, 0] |

## Aggregate Averages

| Method              | Mean Profit | Mean Runtime (s) | Mean Gap |
| ---                 | ---         | ---              | ---      |
| branch_and_bound    | 36.67       | 0.0440           | 0.00     |
| branch_and_cut      | 34.67       | 0.0060           | 2.00     |
| dynamic_programming | 29.67       | 0.0558           | 7.00     |
| genetic_algorithm   | 36.67       | 0.3022           | 0.00     |
| grasp               | 36.67       | 0.0689           | 0.00     |
| tabu_search         | 36.67       | 0.0278           | 0.00     |

## Notes

- `Search Units` corresponds to nodes explored for exact methods and iterations for the metaheuristics.
- `State Steps` is the number of recorded visualization states written into each solution metadata block.
- All artifacts for each run are stored under `outputs/comparative_experiments/<instance>/<method>/`.
