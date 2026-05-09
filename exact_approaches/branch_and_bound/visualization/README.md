"""
Visualization Documentation for Branch and Bound.
Real-time algorithm progression viewer with interactive controls.
"""

# Interactive HTML Viewer Features

The visualization system generates an interactive HTML5 viewer for each B&B run showing:

## Core Visualizations

### 1. **Route Progression Map**
- **Nodes**: 
  - Blue star: Depot (start/end node)
  - Green circles: Visited nodes in current route
  - Gray circles: Unvisited nodes
- **Route**: Blue line connecting visited nodes
- Updates as algorithm progresses through search tree
- Shows final best route at each step

### 2. **Profit Accumulation Chart**
- Real-time line chart showing profit growth
- X-axis: Algorithm step number
- Y-axis: Current profit in best route
- Shaded area under curve
- Updates as better solutions are found

### 3. **Decision Log**
- Step-by-step log of all algorithm decisions
- Color-coded by action type:
  - **Green**: add_node - node added to route
  - **Blue**: close_route - route closed and evaluated
  - **Red**: prune - branch eliminated
  - **Yellow**: update_incumbent - new best solution found
- Shows decision reasoning for each step

## Interactive Controls

### Playback Controls
- **Play**: Animate through all steps automatically
- **Pause**: Pause animation at current step
- **Reset**: Return to initial state (step 0)

### Navigation
- **Step Slider**: Jump to any step in the algorithm
- **Step Counter**: Displays current step / total steps

### Speed Control
- **Speed Slider**: Adjust animation speed (1.5x-0.5x)
- Higher speed = faster animation

## Information Panel

Real-time metrics display:
- **Profit**: Current best profit found
- **Distance**: Current route total distance
- **Nodes Explored**: Total search tree nodes visited
- **Nodes Pruned**: Branches eliminated by pruning

## Data Recorded for Each Step

The viewer receives JSON data with 674 steps for the example instance:

```json
{
  "step_number": int,
  "action": "add_node" | "close_route" | "prune" | "update_incumbent",
  "route": [list of node IDs],
  "current_profit": float,
  "current_cost": float,
  "remaining_budget": float,
  "nodes_explored": int,
  "nodes_pruned": int,
  "decision_reason": string,
  "candidate_nodes": [list of node IDs],
  "best_incumbent_profit": float
}
```

## How to Use

1. **Run the solver**:
   ```bash
   cd Orienteering-Problem-Solver
   python -m exact_approaches.branch_and_bound.run \
     --input instances/shared_test/example_op.json \
     --output outputs/branch_and_bound/example_op_solution.json
   ```

2. **Open the HTML viewer**:
   - Look for `example_op_solution_viewer.html` in output directory
   - Open in any modern web browser (Chrome, Firefox, Safari, Edge)
   - No internet connection required (all rendering is local)

3. **Interact with the visualization**:
   - Click **Play** to watch the algorithm in action
   - Use the slider to jump to any step
   - Adjust speed for viewing preference
   - Monitor metrics in the info panel
   - Read the decision log to understand algorithm choices

## Technical Implementation

- **State Recording**: `state_recorder.py` - captures algorithm intermediate states
- **HTML Generation**: `viewer.py` - creates interactive HTML template
- **Visualization**: Uses Plotly.js for charts and custom canvas for route map
- **Data Embedding**: Algorithm steps embedded as JSON in HTML (no server needed)

## Benefits for Understanding

This real-time visualization helps:
- **Learn B&B algorithm**: See exactly how decisions are made
- **Debug solutions**: Trace why certain branches are pruned
- **Compare instances**: Run different instances and compare progressions
- **Understand trade-offs**: Watch profit vs. distance trade-offs unfold
