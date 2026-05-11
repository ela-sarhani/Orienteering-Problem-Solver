"""HTML viewer for the Genetic Algorithm approach."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from metaheuristic_approaches.common.viewer import generate_html_viewer as _generate_html_viewer


def generate_html_viewer(instance_data: dict[str, Any], algorithm_steps: dict[str, Any], output_path: str | Path) -> None:
    _generate_html_viewer(
        instance_data,
        algorithm_steps,
        output_path,
        title="Genetic Algorithm Progression Viewer",
        description="Interactive playback of the genetic algorithm generations, incumbent updates, and fitness progression.",
    )
