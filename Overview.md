# Overview — Orienteering Problem

## Problem Choice and Justification

**Problem Selected:** Orienteering Problem (OP)

**Rationale:**
The Orienteering Problem was selected because it offers a balanced combination of algorithmic richness, implementation feasibility, and experimental flexibility. 

Another important motivation behind this choice is its suitability for comparative experimentation. The problem can be modeled and visualized naturally on graphs, making it easier to analyze solution quality, route behavior, and algorithmic performance across different approaches. In addition, the problem supports a wide variety of neighborhood structures and search strategies, which makes it particularly appropriate for implementing and evaluating multiple metaheuristic techniques.

Finally, the problem aligns well with modern intelligent systems applications, especially in areas involving autonomous navigation, constrained exploration, and decision-making under limited resources. This makes it technically engaging and relevant to real-world optimization scenarios.

## Combinatorial Structure and Modeling Challenges

**Core Difficulty:**
- The OP's combinatorial explosion arises from two interacting decisions:
  1. **Selection:** which subset of n−1 vertices (excluding start) maximizes profit while staying within distance budget B.
  2. **Ordering:** for a chosen subset, find the shortest route visiting those vertices exactly once and returning to start.
- The number of feasible solutions grows as O(2^n · n!), making exhaustive search impractical even for moderate n.

**Modeling Challenges:**
- The budget constraint couples node selection (y_i) with arc selection (x_ij), creating a non-separable optimization problem.
- Preventing subtours (cycles not including start) requires additional constraints, complicating exact formulations.
- The trade-off between exploration (testing different subsets) and exploitation (optimizing routes for chosen subsets) makes heuristic design non-trivial.

## Why OP is Suitable for Exact and Metaheuristic Study

**Suitability for Exact Methods:**
- Small instances (n ≤ 20–30) can be solved to provable optimality using ILP solvers with branch-and-cut or similar techniques.
- DP formulations exist (on subsets + current node) and give baseline solutions for tiny instances.
- Exact methods provide optimal benchmarks against which heuristics can be measured.

**Suitability for Metaheuristics:**
- Larger instances (n > 50) require heuristic approaches; OP's structure permits efficient neighborhood operators (2-opt, remove-and-insert, node swaps).
- The presence of a clear profit/cost trade-off makes local search effective: greedy moves (add high-profit nodes if budget allows) and moves that sacrifice some cost for profit are natural.
- Multiple independent metaheuristics (tabu search, simulated annealing, GRASP, genetic algorithms, VNS) can be meaningfully compared on the same instances.

## Formal Problem Definition

- **Input:** a weighted undirected complete graph with n vertices, vertex profits, and a distance budget.
- **Decision:** a single route starting and ending at a designated start vertex, visiting a subset of vertices, collecting profit from visited vertices, such that total distance does not exceed B.
- **Objective:** maximize total collected profit.
- **Output:** a feasible tour (or sequence of vertices to visit) and its profit value.

## Sets, Parameters, and Constraints

### Sets and Parameters
- **V** : set of vertices indexed 0..n−1; vertex 0 is the **start** (depot).
- **c_ij ≥ 0** : travel distance (or cost) from vertex i to j, for all i,j ∈ V.
- **p_i ≥ 0** : profit collected upon visiting vertex i. Assume **p_0 = 0** (start has no profit).
- **B > 0** : total travel-distance budget (upper bound on total route distance).

### Core Constraints
1. **Budget Constraint:**
   - Total distance traveled must not exceed B: the sum of all arc distances in the route ≤ B.

2. **Routing Structure:**
   - A single closed route starts and ends at vertex 0 (start).
   - Each visited vertex is entered and exited exactly once (connectivity).

3. **Visit-Once Constraint:**
   - Each vertex can be visited at most once (no repeated visits).

4. **No Subtours:**
   - The route must form a single connected component (no cycles not including start).


## Mathematical Formulation of the Objective

**Objective Function:**

$$\text{Maximize} \quad \sum_{i \in V} p_i \cdot y_i$$

where:
- **y_i** = 1 if vertex i is visited, 0 otherwise.
- **p_i** = profit from vertex i.

**Equivalently (in terms of a solution tour):**

$$\text{Maximize} \quad \sum_{i \in \text{visited}} p_i$$

subject to:
- Distance(tour) ≤ B.
- Tour starts and ends at vertex 0 and visits each selected node exactly once.


## Key Assumptions

- **Graph:** 
    - Complete graph (all pairs of vertices connected). 
    - If using coordinates, c_ij is computed via Euclidean distance.
    - c_ij = c_ji.
- **Costs:** Nonnegative.
- **Profits:** Nonnegative, start/end vertex has zero profit.
- **Route Structure:** Single vehicle, single closed route (depart from start, return to start).


## Approaches

- **Exact Methods:** MIP + B&B (Mixed Integer Programming solved using Branch and Bound), B&C (Branch and Cut), and Dynamic Programming.
- **Metaheuristics:** Genetic Algorithm, Tabu Search, and GRASP.