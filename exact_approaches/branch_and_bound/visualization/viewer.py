"""
HTML Viewer Generator for Algorithm Visualization.
Creates an interactive HTML file that animates algorithm progression in real-time.
Displays route, profit accumulation, decisions, and metrics step-by-step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def generate_html_viewer(
    instance_data: dict[str, Any],
    algorithm_steps: dict[str, Any],
    output_path: str | Path,
) -> None:
    """Generate an interactive HTML viewer for the algorithm progression."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    instance_json = json.dumps(instance_data)
    steps_json = json.dumps(algorithm_steps)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B&B Graph Progression Viewer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Segoe UI", sans-serif; background: #eef3f7; color: #102030; }}
        .container {{ max-width: 1500px; margin: 0 auto; padding: 18px; }}
        .title {{ margin-bottom: 14px; }}
        .title h1 {{ font-size: 24px; margin-bottom: 4px; }}
        .title p {{ color: #3c556a; font-size: 14px; }}
        .controls {{ background: #ffffff; border-radius: 10px; padding: 12px; box-shadow: 0 2px 6px rgba(16,32,48,0.12); margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
        .controls button {{ background: #0a6db8; border: none; color: #fff; padding: 9px 15px; border-radius: 7px; cursor: pointer; }}
        .controls button:disabled {{ background: #9eb6ca; cursor: not-allowed; }}
        .controls input[type="range"] {{ vertical-align: middle; }}
        .kpis {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 12px; }}
        .kpi {{ background: #fff; border-radius: 10px; padding: 10px; box-shadow: 0 2px 6px rgba(16,32,48,0.12); }}
        .kpi .label {{ font-size: 12px; color: #546c80; }}
        .kpi .value {{ font-size: 20px; font-weight: 700; }}
        .layout {{ display: grid; grid-template-columns: 2.3fr 1fr; gap: 12px; }}
        .panel {{ background: #fff; border-radius: 10px; padding: 10px; box-shadow: 0 2px 6px rgba(16,32,48,0.12); }}
        #graphView {{ width: 100%; height: 580px; }}
        #budgetProfitChart {{ width: 100%; height: 260px; margin-top: 8px; }}
        .legend {{ display: flex; gap: 12px; flex-wrap: wrap; font-size: 12px; color: #33495d; margin-top: 8px; }}
        .chip::before {{ content: ""; display: inline-block; width: 18px; height: 3px; margin-right: 6px; vertical-align: middle; }}
        .chip.all::before {{ background: #c7d4df; }}
        .chip.accepted::before {{ background: #1fa56a; }}
        .chip.tested::before {{ background: #ff9f1a; }}
        .chip.pruned::before {{ background: #d7263d; }}
        .outcome {{ line-height: 1.6; font-size: 13px; margin-bottom: 10px; }}
        .decision-log {{ max-height: 640px; overflow-y: auto; font-size: 12px; }}
        .entry {{ border-left: 4px solid #c7d4df; background: #f7fbff; margin-bottom: 8px; padding: 7px; border-radius: 6px; }}
        .entry.add_node {{ border-left-color: #1fa56a; }}
        .entry.prune {{ border-left-color: #d7263d; }}
        .entry.update_incumbent {{ border-left-color: #ff9f1a; }}
        @media (max-width: 1100px) {{
            .kpis {{ grid-template-columns: repeat(3, 1fr); }}
            .layout {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">
            <h1>Branch and Bound Graph Progression</h1>
            <p>Vertices are labeled with profit. Every arc is labeled with travel cost. Step through tested, accepted, and pruned decisions.</p>
        </div>

        <div class="controls">
            <button id="playBtn" onclick="playAnimation()">Play</button>
            <button id="pauseBtn" onclick="pauseAnimation()" disabled>Pause</button>
            <button onclick="resetAnimation()">Reset</button>
            <label>Step</label>
            <input id="stepSlider" type="range" min="0" max="0" value="0" oninput="goToStep(this.value)" style="width: 320px;">
            <span id="stepLabel">0 / 0</span>
            <label style="margin-left: 8px;">Speed</label>
            <input id="speedSlider" type="range" min="100" max="1400" value="600" style="width: 180px;">
        </div>

        <div class="kpis">
            <div class="kpi"><div class="label">Current Profit</div><div class="value" id="profitValue">0.00</div></div>
            <div class="kpi"><div class="label">Remaining Budget</div><div class="value" id="budgetValue">0.00</div></div>
            <div class="kpi"><div class="label">Current Route Cost</div><div class="value" id="costValue">0.00</div></div>
            <div class="kpi"><div class="label">Incumbent Profit</div><div class="value" id="incumbentValue">0.00</div></div>
            <div class="kpi"><div class="label">Nodes Explored</div><div class="value" id="exploredValue">0</div></div>
            <div class="kpi"><div class="label">Nodes Pruned</div><div class="value" id="prunedValue">0</div></div>
        </div>

        <div class="layout">
            <div class="panel">
                <div id="graphView"></div>
                <div id="budgetProfitChart"></div>
                <div class="legend">
                    <span class="chip all">all arcs</span>
                    <span class="chip accepted">accepted path arcs</span>
                    <span class="chip tested">currently tested arc</span>
                    <span class="chip pruned">pruned/test-failed arc</span>
                </div>
            </div>
            <div class="panel">
                <div style="background: #fffbf0; border-left: 5px solid #ff9f1a; padding: 10px; border-radius: 6px; margin-bottom: 12px;">
                    <h3 style="margin: 0 0 8px 0; color: #ff7200; font-size: 16px;">🏆 Best Solution Found</h3>
                    <div style="background: #fff; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 13px; margin-bottom: 6px;">
                        <div><strong>Route:</strong> <span id="bestRoute">—</span></div>
                        <div><strong>Profit:</strong> <span id="bestProfit">0.00</span> / <span id="budgetLabel">0.00</span></div>
                        <div><strong>Cost:</strong> <span id="bestCost">0.00</span></div>
                        <div><strong>Nodes:</strong> <span id="bestNodes">0</span></div>
                    </div>
                    <div style="font-size: 11px; color: #666; line-height: 1.4;">
                        Found at: <span id="bestFoundAt">step 1</span><br/>
                        Still best: <span id="bestStatus">✓ Optimal</span>
                    </div>
                </div>

                <h3 style="margin-bottom:8px;">Step Outcome</h3>
                <div class="outcome" id="outcomeBox"></div>
                <h3 style="margin: 8px 0;">Decision Log (latest first)</h3>
                <div class="decision-log" id="decisionLog"></div>
            </div>
        </div>
    </div>

    <script>
        const instanceData = {instance_json};
        const algorithmSteps = {steps_json};

        const nodes = (instanceData.visualization && instanceData.visualization.nodes) || [];
        const nodeById = new Map(nodes.map((n) => [n.id, n]));
        const costMatrix = instanceData.cost_matrix || [];
        const totalBudget = instanceData.budget || 0;

        let currentStep = 0;
        let isPlaying = false;
        let playTimeout = null;

        function edgeKey(a, b) {{
            return a < b ? `${{a}}-${{b}}` : `${{b}}-${{a}}`;
        }}

        function routeEdges(route) {{
            const edges = [];
            for (let i = 0; i < route.length - 1; i++) {{
                edges.push([route[i], route[i + 1]]);
            }}
            return edges;
        }}

        function stepDelta(stepIndex, field) {{
            if (stepIndex <= 0) return algorithmSteps.steps[stepIndex][field] || 0;
            const prev = algorithmSteps.steps[stepIndex - 1][field] || 0;
            const curr = algorithmSteps.steps[stepIndex][field] || 0;
            return curr - prev;
        }}

        function deriveStepContext(step) {{
            const accepted = routeEdges(step.route || []);
            let tested = null;
            let pruned = null;

            if (step.action === "add_node" && step.route && step.route.length >= 2) {{
                tested = [step.route[step.route.length - 2], step.route[step.route.length - 1]];
            }}

            if (step.action === "prune" && step.candidate_nodes && step.candidate_nodes.length > 0 && step.route && step.route.length >= 1) {{
                const fromNode = step.route[step.route.length - 1];
                pruned = [fromNode, step.candidate_nodes[0]];
            }}

            return {{ accepted, tested, pruned }};
        }}

        function buildBaseEdgeTraces() {{
            const traces = [];
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    const ni = nodes[i];
                    const nj = nodes[j];
                    traces.push({{
                        x: [ni.x, nj.x],
                        y: [ni.y, nj.y],
                        mode: "lines",
                        type: "scatter",
                        hoverinfo: "skip",
                        line: {{ color: "#c7d4df", width: 1 }},
                        showlegend: false,
                    }});
                }}
            }}
            return traces;
        }}

        function buildEdgeCostAnnotations() {{
            const annotations = [];
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    const ni = nodes[i];
                    const nj = nodes[j];
                    const midX = (ni.x + nj.x) / 2;
                    const midY = (ni.y + nj.y) / 2;
                    const cost = costMatrix[i] && costMatrix[i][j] !== undefined ? costMatrix[i][j] : NaN;
                    annotations.push({{
                        x: midX,
                        y: midY,
                        text: isNaN(cost) ? "-" : cost.toFixed(2),
                        font: {{ size: 9, color: "#607b91" }},
                        showarrow: false,
                        bgcolor: "rgba(255,255,255,0.72)",
                    }});
                }}
            }}
            return annotations;
        }}

        function buildHighlightTrace(edge, color, width, dash = "solid") {{
            if (!edge) return null;
            const a = nodeById.get(edge[0]);
            const b = nodeById.get(edge[1]);
            if (!a || !b) return null;
            return {{
                x: [a.x, b.x],
                y: [a.y, b.y],
                mode: "lines",
                type: "scatter",
                hoverinfo: "skip",
                line: {{ color, width, dash }},
                showlegend: false,
            }};
        }}

        function buildNodeTrace(visitedSet) {{
            const x = [];
            const y = [];
            const text = [];
            const colors = [];
            const sizes = [];
            const symbols = [];

            for (const n of nodes) {{
                x.push(n.x);
                y.push(n.y);
                text.push(`v${{n.id}} | p=${{Number(n.profit).toFixed(1)}}`);
                if (n.id === 0) {{
                    colors.push("#0a6db8");
                    sizes.push(20);
                    symbols.push("star");
                }} else if (visitedSet.has(n.id)) {{
                    colors.push("#1fa56a");
                    sizes.push(16);
                    symbols.push("circle");
                }} else {{
                    colors.push("#8ea5b8");
                    sizes.push(13);
                    symbols.push("circle");
                }}
            }}

            return {{
                x,
                y,
                mode: "markers+text",
                type: "scatter",
                text,
                textposition: "top center",
                marker: {{ color: colors, size: sizes, symbol: symbols, line: {{ color: "#20384d", width: 1 }} }},
                hovertemplate: "%{{text}}<extra></extra>",
                showlegend: false,
            }};
        }}

        function updateGraph(step) {{
            if (!nodes.length) return;

            const visited = new Set((step.route || []).slice(1, -1));
            const ctx = deriveStepContext(step);
            const acceptedKeys = new Set(ctx.accepted.map((e) => edgeKey(e[0], e[1])));

            const traces = [];
            traces.push(...buildBaseEdgeTraces());

            for (const e of ctx.accepted) {{
                const t = buildHighlightTrace(e, "#1fa56a", 4, "solid");
                if (t) traces.push(t);
            }}

            if (ctx.pruned && !acceptedKeys.has(edgeKey(ctx.pruned[0], ctx.pruned[1]))) {{
                const t = buildHighlightTrace(ctx.pruned, "#d7263d", 4, "dash");
                if (t) traces.push(t);
            }}

            if (ctx.tested && !acceptedKeys.has(edgeKey(ctx.tested[0], ctx.tested[1]))) {{
                const t = buildHighlightTrace(ctx.tested, "#ff9f1a", 4, "solid");
                if (t) traces.push(t);
            }}

            traces.push(buildNodeTrace(visited));

            const layout = {{
                title: `Graph State at Step ${{step.step_number}}`,
                xaxis: {{ title: "x", zeroline: false }},
                yaxis: {{ title: "y", zeroline: false, scaleanchor: "x", scaleratio: 1 }},
                margin: {{ l: 40, r: 20, t: 40, b: 35 }},
                paper_bgcolor: "#ffffff",
                plot_bgcolor: "#ffffff",
                annotations: buildEdgeCostAnnotations(),
            }};

            Plotly.react("graphView", traces, layout, {{ responsive: true, displayModeBar: false }});
        }}

        function updateBudgetProfitChart() {{
            const xs = algorithmSteps.steps.map((s) => s.step_number).slice(0, currentStep + 1);
            const profits = algorithmSteps.steps.map((s) => s.current_profit).slice(0, currentStep + 1);
            const remain = algorithmSteps.steps.map((s) => s.remaining_budget).slice(0, currentStep + 1);

            const tProfit = {{
                x: xs,
                y: profits,
                mode: "lines+markers",
                type: "scatter",
                name: "profit",
                line: {{ color: "#1fa56a", width: 2 }},
                yaxis: "y1",
            }};
            const tBudget = {{
                x: xs,
                y: remain,
                mode: "lines+markers",
                type: "scatter",
                name: "remaining budget",
                line: {{ color: "#0a6db8", width: 2 }},
                yaxis: "y2",
            }};

            const layout = {{
                title: "Profit Increase and Budget Decrease",
                xaxis: {{ title: "step" }},
                yaxis: {{ title: "profit", side: "left" }},
                yaxis2: {{ title: "remaining budget", overlaying: "y", side: "right" }},
                margin: {{ l: 45, r: 45, t: 36, b: 36 }},
                legend: {{ orientation: "h", y: 1.18 }},
            }};

            Plotly.react("budgetProfitChart", [tProfit, tBudget], layout, {{ responsive: true, displayModeBar: false }});
        }}

        function updateOutcome(step) {{
            const ctx = deriveStepContext(step);
            const dProfit = stepDelta(currentStep, "current_profit");
            const dBudget = stepDelta(currentStep, "remaining_budget");

            let testedTxt = "none";
            let prunedTxt = "none";

            if (ctx.tested) testedTxt = `${{ctx.tested[0]}} -> ${{ctx.tested[1]}}`;
            if (ctx.pruned) prunedTxt = `${{ctx.pruned[0]}} -> ${{ctx.pruned[1]}}`;

            document.getElementById("outcomeBox").innerHTML =
                `<b>Action:</b> ${{step.action}}<br>` +
                `<b>Route:</b> [${{(step.route || []).join(", ")}}]<br>` +
                `<b>Tested Arc:</b> ${{testedTxt}}<br>` +
                `<b>Pruned Arc:</b> ${{prunedTxt}}<br>` +
                `<b>Delta Profit:</b> ${{dProfit.toFixed(2)}}<br>` +
                `<b>Delta Remaining Budget:</b> ${{dBudget.toFixed(2)}}<br>` +
                `<b>Reason:</b> ${{step.decision_reason || "-"}}`;
        }}

        function updateDecisionLog() {{
            const log = document.getElementById("decisionLog");
            log.innerHTML = "";

            algorithmSteps.steps.slice(0, currentStep + 1).reverse().forEach((s) => {{
                const i = s.step_number - 1;
                const dp = i >= 0 ? stepDelta(i, "current_profit") : 0;
                const db = i >= 0 ? stepDelta(i, "remaining_budget") : 0;
                const entry = document.createElement("div");
                entry.className = `entry ${{s.action}}`;
                entry.innerHTML =
                    `<b>#${{s.step_number}} ${{s.action}}</b><br>` +
                    `route=[${{(s.route || []).join(", ")}}]<br>` +
                    `profit=${{Number(s.current_profit).toFixed(2)}} (delta ${{dp.toFixed(2)}}), ` +
                    `remaining_budget=${{Number(s.remaining_budget).toFixed(2)}} (delta ${{db.toFixed(2)}})<br>` +
                    `reason: ${{s.decision_reason || "-"}}`;
                log.appendChild(entry);
            }});
        }}

        function updateKpis(step) {{
            document.getElementById("profitValue").textContent = Number(step.current_profit).toFixed(2);
            document.getElementById("budgetValue").textContent = Number(step.remaining_budget).toFixed(2);
            document.getElementById("costValue").textContent = Number(step.current_cost).toFixed(2);
            document.getElementById("incumbentValue").textContent = Number(step.best_incumbent_profit).toFixed(2);
            document.getElementById("exploredValue").textContent = step.nodes_explored;
            document.getElementById("prunedValue").textContent = step.nodes_pruned;
            document.getElementById("stepLabel").textContent = `${{currentStep + 1}} / ${{algorithmSteps.total_steps}}`;
        }}

        let bestSolutionCache = {{
            profit: instanceData.best_profit || 0,
            route: instanceData.best_route || [0, 0],
            cost: instanceData.best_cost || 0,
            foundAt: -1,  // -1 means not yet found in state_history
        }};

        function computeRouteCost(route) {{
            let cost = 0;
            for (let i = 0; i < route.length - 1; i++) {{
                const from = route[i];
                const to = route[i + 1];
                if (costMatrix[from] && costMatrix[from][to] !== undefined) {{
                    cost += costMatrix[from][to];
                }}
            }}
            return cost;
        }}

        function isCompleteRoute(route) {{
            return route && route.length >= 2 && route[0] === 0 && route[route.length - 1] === 0;
        }}

        function updateBestSolution(step) {{
            // On first call, find when the best solution was actually discovered in state_history
            if (bestSolutionCache.foundAt === -1) {{
                const targetProfit = bestSolutionCache.profit;
                const targetRoute = JSON.stringify(bestSolutionCache.route);
                
                for (let i = 0; i <= currentStep; i++) {{
                    const s = algorithmSteps.steps[i];
                    if (s.best_incumbent_profit === targetProfit) {{
                        const route = s.route || [];
                        if (isCompleteRoute(route) && JSON.stringify(route) === targetRoute) {{
                            bestSolutionCache.foundAt = s.step_number;
                            break;
                        }}
                    }}
                }}
                
                // If not found in state_history, it was found during initialization
                if (bestSolutionCache.foundAt === -1) {{
                    bestSolutionCache.foundAt = 0;
                }}
            }}

            const numNodes = Math.max(0, bestSolutionCache.route.length - 2);
            const routeStr = bestSolutionCache.route.join(" → ");

            document.getElementById("bestRoute").textContent = routeStr;
            document.getElementById("bestProfit").textContent = Number(bestSolutionCache.profit).toFixed(2);
            document.getElementById("budgetLabel").textContent = totalBudget.toFixed(2);
            document.getElementById("bestCost").textContent = Number(bestSolutionCache.cost).toFixed(2);
            document.getElementById("bestNodes").textContent = numNodes;
            document.getElementById("bestFoundAt").textContent = 
                bestSolutionCache.foundAt === 0 ? "step 0 (init)" : `step ${{bestSolutionCache.foundAt}}`;
            document.getElementById("bestStatus").textContent = "✓ Optimal";
        }}


        function updateVisualization() {{
            if (!algorithmSteps.steps || algorithmSteps.steps.length === 0) return;
            const step = algorithmSteps.steps[currentStep];
            updateKpis(step);
            updateBestSolution(step);
            updateGraph(step);
            updateBudgetProfitChart();
            updateOutcome(step);
            updateDecisionLog();
            const slider = document.getElementById("stepSlider");
            slider.max = algorithmSteps.total_steps - 1;
            slider.value = currentStep;
        }}

        function playAnimation() {{
            isPlaying = true;
            document.getElementById("playBtn").disabled = true;
            document.getElementById("pauseBtn").disabled = false;
            animateStep();
        }}

        function pauseAnimation() {{
            isPlaying = false;
            document.getElementById("playBtn").disabled = false;
            document.getElementById("pauseBtn").disabled = true;
            if (playTimeout) clearTimeout(playTimeout);
        }}

        function resetAnimation() {{
            pauseAnimation();
            currentStep = 0;
            updateVisualization();
        }}

        function animateStep() {{
            if (!isPlaying) return;
            if (currentStep < algorithmSteps.total_steps - 1) {{
                currentStep += 1;
                updateVisualization();
                const speed = Number(document.getElementById("speedSlider").value);
                const delay = Math.max(90, 1550 - speed);
                playTimeout = setTimeout(animateStep, delay);
            }} else {{
                pauseAnimation();
            }}
        }}

        function goToStep(step) {{
            currentStep = Number(step);
            updateVisualization();
        }}

        updateVisualization();
    </script>
</body>
</html>
"""

    output_path.write_text(html_content, encoding="utf-8")
