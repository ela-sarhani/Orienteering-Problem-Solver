"""Generate a single landing page to navigate all OP viewers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


ViewerEntry = tuple[str, str]


def generate_viewer_hub(
    output_path: str | Path,
    *,
    exact_viewers: list[ViewerEntry],
    metaheuristic_viewers: list[ViewerEntry],
    title: str = "Orienteering Problem Viewer Hub",
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    default_viewer = exact_viewers[0][1] if exact_viewers else (metaheuristic_viewers[0][1] if metaheuristic_viewers else "about:blank")

    exact_opts = "".join(f'<option value="{path}">{label}</option>' for label, path in exact_viewers)
    meta_opts = "".join(f'<option value="{path}">{label}</option>' for label, path in metaheuristic_viewers)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #f5f5f5; }}
    .bar {{ background: #fff; padding: 12px 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
    .title {{ font-size: 13px; font-weight: 600; color: #333; margin-right: 8px; }}
    .controls {{ display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; }}
    .control-item {{ display: flex; flex-direction: column; gap: 4px; }}
    .control-label {{ font-size: 11px; font-weight: 600; color: #555; text-transform: uppercase; }}
    select {{ padding: 6px 8px; font-size: 12px; border: 1px solid #999; border-radius: 4px; cursor: pointer; min-width: 160px; background: #fff; }}
    select:focus {{ outline: none; border-color: #0066cc; box-shadow: 0 0 0 2px rgba(0,102,204,0.15); }}
    iframe {{ width: 100%; height: calc(100vh - 50px); border: none; }}
  </style>
</head>
<body>
  <div class="bar">
    <div class="title">Choose the approach:</div>
    <div class="controls">
      <div class="control-item">
        <div class="control-label">Exact</div>
        <select id="exact" onchange="upd()"><option>-</option>{exact_opts}</select>
      </div>
      <div class="control-item">
        <div class="control-label">Metaheuristic</div>
        <select id="meta" onchange="upd()"><option>-</option>{meta_opts}</select>
      </div>
    </div>
  </div>
  <iframe id="frame" src="{default_viewer}"></iframe>
  <script>
    const e=document.getElementById('exact'),m=document.getElementById('meta'),f=document.getElementById('frame');
    document.getElementById('exact').value='{default_viewer}';
    function upd(){{const v=e.value||m.value;if(v){{f.src=v;e.value===v?m.value='':e.value=''}}}}
  </script>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
