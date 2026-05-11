"""Shared HTML viewer generator for metaheuristic solvers."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def generate_html_viewer(
    instance_data: dict[str, Any],
    algorithm_steps: dict[str, Any],
    output_path: str | Path,
    *,
    title: str,
    description: str,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    instance_json = json.dumps(instance_data)
    steps_json = json.dumps(algorithm_steps)

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{title}</title>
  <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: linear-gradient(135deg, #eef4f8, #f7f1e8); color: #152433; }}
    .container {{ max-width: 1500px; margin: 0 auto; padding: 18px; }}
    .hero {{ background: rgba(255,255,255,0.85); border: 1px solid rgba(21,36,51,0.08); border-radius: 18px; padding: 16px 18px; box-shadow: 0 10px 30px rgba(21,36,51,0.08); margin-bottom: 14px; }}
    .hero h1 {{ margin: 0 0 6px 0; font-size: 26px; }}
    .hero p {{ margin: 0; color: #4d657b; line-height: 1.45; }}
    .controls, .panel {{ background: rgba(255,255,255,0.95); border-radius: 16px; box-shadow: 0 10px 30px rgba(21,36,51,0.08); border: 1px solid rgba(21,36,51,0.06); }}
    .controls {{ padding: 12px 14px; margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
    button {{ background: #1d70b8; color: white; border: 0; border-radius: 10px; padding: 9px 15px; cursor: pointer; font-weight: 600; }}
    button:disabled {{ background: #9fb7cb; cursor: not-allowed; }}
    .kpis {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 12px; }}
    .kpi {{ padding: 10px 12px; border-radius: 14px; background: rgba(255,255,255,0.94); border: 1px solid rgba(21,36,51,0.07); box-shadow: 0 8px 18px rgba(21,36,51,0.05); }}
    .kpi .label {{ color: #5a7084; font-size: 12px; }}
    .kpi .value {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
    .layout {{ display: grid; grid-template-columns: 2.2fr 1fr; gap: 12px; }}
    .panel {{ padding: 12px; }}
    #graphView {{ width: 100%; height: 560px; }}
    #trendChart {{ width: 100%; height: 250px; margin-top: 10px; }}
    .decision-log {{ max-height: 650px; overflow: auto; font-size: 12px; }}
    .entry {{ border-left: 4px solid #c7d4df; padding: 8px 10px; margin-bottom: 8px; border-radius: 10px; background: #f8fbfe; }}
    .entry.improve {{ border-left-color: #1b9a59; }}
    .entry.iteration {{ border-left-color: #1d70b8; }}
    .entry.prune {{ border-left-color: #d22e47; }}
    .best-box {{ background: linear-gradient(135deg, #fff8e9, #fffdf5); border: 1px solid #f0cf82; border-left: 6px solid #f4a100; border-radius: 14px; padding: 12px; margin-bottom: 12px; }}
    .best-box h3 {{ margin: 0 0 8px 0; color: #c36d00; }}
    .best-box .small {{ font-size: 11px; color: #6b6b6b; line-height: 1.45; }}
    @media (max-width: 1100px) {{ .kpis {{ grid-template-columns: repeat(3, 1fr); }} .layout {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class=\"container\">
    <div class=\"hero\">
      <h1>{title}</h1>
      <p>{description}</p>
    </div>

    <div class=\"controls\">
      <button id=\"playBtn\" onclick=\"playAnimation()\">Play</button>
      <button id=\"pauseBtn\" onclick=\"pauseAnimation()\" disabled>Pause</button>
      <button onclick=\"resetAnimation()\">Reset</button>
      <label>Step</label>
      <input id=\"stepSlider\" type=\"range\" min=\"0\" max=\"0\" value=\"0\" oninput=\"goToStep(this.value)\" style=\"width: 320px;\" />
      <span id=\"stepLabel\">0 / 0</span>
      <label>Speed</label>
      <input id=\"speedSlider\" type=\"range\" min=\"100\" max=\"1400\" value=\"650\" style=\"width: 180px;\" />
    </div>

    <div class=\"kpis\">
      <div class=\"kpi\"><div class=\"label\">Current Profit</div><div class=\"value\" id=\"profitValue\">0.00</div></div>
      <div class=\"kpi\"><div class=\"label\">Remaining Budget</div><div class=\"value\" id=\"budgetValue\">0.00</div></div>
      <div class=\"kpi\"><div class=\"label\">Current Route Cost</div><div class=\"value\" id=\"costValue\">0.00</div></div>
      <div class=\"kpi\"><div class=\"label\">Best Incumbent</div><div class=\"value\" id=\"incumbentValue\">0.00</div></div>
      <div class=\"kpi\"><div class=\"label\">Iterations</div><div class=\"value\" id=\"iterationsValue\">0</div></div>
      <div class=\"kpi\"><div class=\"label\">Candidates Evaluated</div><div class=\"value\" id=\"evaluatedValue\">0</div></div>
    </div>

    <div class=\"layout\">
      <div class=\"panel\">
        <div id=\"graphView\"></div>
        <div id=\"trendChart\"></div>
      </div>
      <div class=\"panel\">
        <div class=\"best-box\">
          <h3>Best Solution Found</h3>
          <div style=\"background:#fff; padding:10px; border-radius:10px; font-family: monospace; font-size:13px;\">
            <div><strong>Route:</strong> <span id=\"bestRoute\">—</span></div>
            <div><strong>Profit:</strong> <span id=\"bestProfit\">0.00</span> / <span id=\"budgetLabel\">0.00</span></div>
            <div><strong>Cost:</strong> <span id=\"bestCost\">0.00</span></div>
            <div><strong>Nodes:</strong> <span id=\"bestNodes\">0</span></div>
          </div>
          <div class=\"small\">Found at: <span id=\"bestFoundAt\">step 0</span><br />Best-so-far route is updated whenever a better feasible tour is found.</div>
        </div>
        <h3 style=\"margin: 10px 0 6px 0;\">Step Outcome</h3>
        <div id=\"outcomeBox\" style=\"font-size: 13px; line-height: 1.55; margin-bottom: 10px;\"></div>
        <h3 style=\"margin: 0 0 6px 0;\">Decision Log</h3>
        <div class=\"decision-log\" id=\"decisionLog\"></div>
      </div>
    </div>
  </div>

  <script>
    const instanceData = {instance_json};
    const algorithmSteps = {steps_json};
    const nodes = (instanceData.visualization && instanceData.visualization.nodes) || [];
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const costMatrix = instanceData.cost_matrix || [];
    const totalBudget = instanceData.budget || 0;

    let currentStep = 0;
    let isPlaying = false;
    let playTimeout = null;

    function routeEdges(route) {{
      const edges = [];
      for (let index = 0; index < route.length - 1; index++) edges.push([route[index], route[index + 1]]);
      return edges;
    }}

    function buildEdgeTrace(edge, color, width, dash = 'solid') {{
      if (!edge) return null;
      const a = nodeById.get(edge[0]);
      const b = nodeById.get(edge[1]);
      if (!a || !b) return null;
      return {{ x: [a.x, b.x], y: [a.y, b.y], mode: 'lines', type: 'scatter', hoverinfo: 'skip', line: {{ color, width, dash }}, showlegend: false }};
    }}

    function buildNodeTrace(visitedSet) {{
      const x = [], y = [], text = [], colors = [], sizes = [], symbols = [];
      for (const node of nodes) {{
        x.push(node.x);
        y.push(node.y);
        text.push(`v${{node.id}} | p=${{Number(node.profit).toFixed(1)}}`);
        if (node.id === 0) {{ colors.push('#1d70b8'); sizes.push(20); symbols.push('star'); }}
        else if (visitedSet.has(node.id)) {{ colors.push('#1b9a59'); sizes.push(16); symbols.push('circle'); }}
        else {{ colors.push('#97a9b8'); sizes.push(13); symbols.push('circle'); }}
      }}
      return {{ x, y, mode: 'markers+text', type: 'scatter', text, textposition: 'top center', marker: {{ color: colors, size: sizes, symbol: symbols, line: {{ color: '#20384d', width: 1 }} }}, hovertemplate: '%{{text}}<extra></extra>', showlegend: false }};
    }}

    function buildGraph(step) {{
      const traces = [];
      for (let i = 0; i < nodes.length; i++) {{
        for (let j = i + 1; j < nodes.length; j++) {{
          const ni = nodes[i], nj = nodes[j];
          traces.push({{ x: [ni.x, nj.x], y: [ni.y, nj.y], mode: 'lines', type: 'scatter', hoverinfo: 'skip', line: {{ color: '#d0dbe6', width: 1 }}, showlegend: false }});
        }}
      }}
      for (const edge of routeEdges(step.route || [])) {{
        const t = buildEdgeTrace(edge, '#1d70b8', 4);
        if (t) traces.push(t);
      }}
      traces.push(buildNodeTrace(new Set((step.route || []).slice(1, -1))));
      return traces;
    }}

    function updateTrendChart() {{
      const history = algorithmSteps.steps.slice(0, currentStep + 1);
      const xs = history.map((step) => step.step_number);
      const profits = history.map((step) => step.current_profit);
      const incumbent = history.map((step) => step.best_incumbent_profit);
      const evaluations = history.map((step) => step.candidate_evaluations);
      const layout = {{ title: 'Profit Progression', xaxis: {{ title: 'step' }}, yaxis: {{ title: 'profit' }}, margin: {{ l: 45, r: 20, t: 35, b: 35 }}, legend: {{ orientation: 'h' }} }};
      Plotly.react('trendChart', [
        {{ x: xs, y: profits, mode: 'lines+markers', type: 'scatter', name: 'current profit', line: {{ color: '#1d70b8', width: 2 }} }},
        {{ x: xs, y: incumbent, mode: 'lines+markers', type: 'scatter', name: 'best incumbent', line: {{ color: '#1b9a59', width: 2 }} }},
        {{ x: xs, y: evaluations, mode: 'lines', type: 'scatter', name: 'evaluations', line: {{ color: '#f4a100', width: 2 }}, yaxis: 'y2' }}
      ], {{ ...layout, yaxis2: {{ title: 'evaluations', overlaying: 'y', side: 'right' }} }}, {{ responsive: true, displayModeBar: false }});
    }}

    function isCompleteRoute(route) {{
      return Array.isArray(route) && route.length >= 2 && route[0] === 0 && route[route.length - 1] === 0;
    }}

    function updateBestSolution(step) {{
      const bestRoute = instanceData.best_route || [0, 0];
      document.getElementById('bestRoute').textContent = bestRoute.join(' → ');
      document.getElementById('bestProfit').textContent = Number(instanceData.best_profit || 0).toFixed(2);
      document.getElementById('budgetLabel').textContent = Number(totalBudget).toFixed(2);
      document.getElementById('bestCost').textContent = Number(instanceData.best_cost || 0).toFixed(2);
      document.getElementById('bestNodes').textContent = Math.max(0, bestRoute.length - 2);

      // Find first occurrence of the best route up to the current playback step
      const historySlice = algorithmSteps.steps.slice(0, currentStep + 1);
      const foundStep = historySlice.find((candidate) => isCompleteRoute(candidate.route || []) && JSON.stringify(candidate.route || []) === JSON.stringify(bestRoute));
      document.getElementById('bestFoundAt').textContent = foundStep ? `step ${{foundStep.step_number}}` : 'not found yet';
    }}

    function updateKpis(step) {{
      document.getElementById('profitValue').textContent = Number(step.current_profit).toFixed(2);
      document.getElementById('budgetValue').textContent = Number(step.remaining_budget).toFixed(2);
      document.getElementById('costValue').textContent = Number(step.current_cost).toFixed(2);
      document.getElementById('incumbentValue').textContent = Number(step.best_incumbent_profit).toFixed(2);
      document.getElementById('iterationsValue').textContent = step.iterations;
      document.getElementById('evaluatedValue').textContent = step.candidate_evaluations;
      document.getElementById('stepLabel').textContent = `${{currentStep + 1}} / ${{algorithmSteps.total_steps}}`;
    }}

    function updateOutcome(step) {{
      document.getElementById('outcomeBox').innerHTML =
        `<b>Action:</b> ${{step.action}}<br>` +
        `<b>Route:</b> [${{(step.route || []).join(', ')}}]<br>` +
        `<b>Reason:</b> ${{step.decision_reason || '-'}}`;
    }}

    function updateDecisionLog() {{
      const log = document.getElementById('decisionLog');
      log.innerHTML = '';
      algorithmSteps.steps.slice(0, currentStep + 1).reverse().forEach((step) => {{
        const entry = document.createElement('div');
        entry.className = `entry ${{step.action.includes('improve') ? 'improve' : step.action === 'iteration' ? 'iteration' : step.action === 'prune' ? 'prune' : ''}}`;
        entry.innerHTML = `<b>#${{step.step_number}} ${{step.action}}</b><br>route=[${{(step.route || []).join(', ')}}]<br>profit=${{Number(step.current_profit).toFixed(2)}}, cost=${{Number(step.current_cost).toFixed(2)}}, remaining_budget=${{Number(step.remaining_budget).toFixed(2)}}<br>reason: ${{step.decision_reason || '-'}}`;
        log.appendChild(entry);
      }});
    }}

    function updateVisualization() {{
      if (!algorithmSteps.steps || algorithmSteps.steps.length === 0) return;
      const step = algorithmSteps.steps[currentStep];
      updateKpis(step);
      updateBestSolution(step);
      Plotly.react('graphView', buildGraph(step), {{
        title: `Iteration ${{step.iterations}}`,
        xaxis: {{ title: 'x' }},
        yaxis: {{ title: 'y', scaleanchor: 'x', scaleratio: 1 }},
        margin: {{ l: 40, r: 20, t: 40, b: 35 }},
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff',
      }}, {{ responsive: true, displayModeBar: false }});
      updateTrendChart();
      updateOutcome(step);
      updateDecisionLog();
      document.getElementById('stepSlider').max = algorithmSteps.total_steps - 1;
      document.getElementById('stepSlider').value = currentStep;
    }}

    function playAnimation() {{
      isPlaying = true;
      document.getElementById('playBtn').disabled = true;
      document.getElementById('pauseBtn').disabled = false;
      animateStep();
    }}

    function pauseAnimation() {{
      isPlaying = false;
      document.getElementById('playBtn').disabled = false;
      document.getElementById('pauseBtn').disabled = true;
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
        const speed = Number(document.getElementById('speedSlider').value);
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

    output_path.write_text(html, encoding="utf-8")
