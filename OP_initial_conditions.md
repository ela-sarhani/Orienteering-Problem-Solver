# Initial Conditions & Constraints

Purpose: declare the formal model, assumptions, instance format and environment settings before implementing algorithms.

## 1. Problem identification
- Name: Orienteering Problem (OP)
- Single route starting at `start` city and ending at `end` city.
- Goal: maximize total collected profit from n cities under a total distance limit `B`.

## 2. Required sets and parameters
- `V`: set of vertices (indexed 0..n-1). Vertex 0 is the depot by default.
- `V\{0\}`: candidate vertices with profit.
- `c_ij`: distance from vertex `i` to `j` (nonnegative).
- `p_i`: profit collected when visiting vertex `i` (nonnegative). `p_0 = 0`.
- `B`: total travel budget distance.

## 3. Decision variables (example ILP)
- `x_ij` in {0,1}: arc (i->j) used in the route.
- `y_i` in {0,1}: vertex `i` is visited (collected).
- `u_i` continuous/integer: position/order variable for subtour elimination (if using MTZ).

## 4. Objective
- Maximize sum_{i in V} p_i * y_i subject to budget and route feasibility.

## 5. Core constraints (must include / decide on these)
- Budget constraint: sum_{i,j} c_ij * x_ij + sum_i t_i*y_i <= B.
- Flow constraints: for all i != depot, sum_j x_ji = y_i and sum_j x_ij = y_i (entry=exit=visit).
- Depot constraints: sum_j x_0j = 1 and sum_i x_i0 = 1 (single route) — or adapt for open route.
- Visit-once: y_i in {0,1} and visited at most once.
- Subtour elimination: choose method (MTZ order variables, or flow-based, or B&B with callbacks).

## 6. Optional/advanced constraints (decide if needed)
- Time windows: earliest `a_i` / latest `b_i` arrival times.
- Minimum/maximum number of visited nodes.
- Precedence constraints: i must be visited before j.
- Forbidden arcs/nodes.
- Multiple vehicles (becomes Team Orienteering / multiple routes) — out of scope unless chosen.

## 7. Graph and metric assumptions (pick and record)
- Graph: complete vs sparse. If sparse, specify how missing arcs are handled.
- Metric: Euclidean, Manhattan, or arbitrary asymmetric cost matrix.
- Symmetry: are c_ij == c_ji? (record true/false)

## 8. Instance file format (example JSON)
{
  "n": 10,
  "depot": 0,
  "coords": [[x0,y0],[x1,y1],...],
  "profits": [0, 5, 10, ...],
  "cost_matrix": [[0, ...],[...]],
  "budget": 100.0,
  "service_times": [0, ...],
  "seed": 42
}

Notes:
- If `coords` are provided, compute `c_ij` using chosen metric.
- `cost_matrix` can be given directly for arbitrary costs.

## 9. Instance generator parameters to decide
- Number of nodes `n` (include depot)
- Coordinate bounds (for Euclidean): `xmin,xmax,ymin,ymax`
- Profit distribution (uniform, normal, custom)
- Budget scaling policy: absolute value or fraction of TSP cost (e.g., 0.4 * MST or 0.6 * shortest Hamiltonian)
- Random seed for reproducibility

## 10. Testing instance sizes (suggested)
- Tiny: n = 6–10 (debugging)
- Small: n = 20–50 (unit evaluation)
- Medium: n = 100–200 (algorithm comparison)
- Large: n >= 500 (stress tests for metaheuristics)

## 11. Environment & reproducibility
- Python version: 3.11 (use virtualenv)
- Minimum packages: `numpy`, `scipy`, `networkx`, `pulp` or `ortools` (for ILP), `matplotlib` (optional)
- Record `seed` and random generator used for each experiment.

## 12. Evaluation protocol (what to record)
- Solution value (total profit)
- Total cost (distance/time)
- Running time (CPU time)
- Gap to optimum (if known) or best-known
- Number of nodes visited
- Parameter settings for metaheuristics

## 13. Deliverables checklist (project start)
- [ ] A filled version of this file with chosen assumptions and parameters.
- [ ] Instance generator script and 5 initial instances (one per size above).
- [ ] Data loader that reads the instance JSON and builds `c_ij` and `p_i` structures.

---
Fill the sections above with your choices. Once you confirm the assumptions you want, I can:

- scaffold a Python project with an instance generator, data loader and a minimal solver harness,
- or draft the formal ILP formulation in LaTeX/Math form based on your chosen subtour elimination method.
