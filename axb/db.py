from uuid import uuid4
import json
from pathlib import Path
from typing import Dict

from axb.axclient import _AxClient

EXPERIMENT_DIR = Path("experiments")
EXPERIMENT_DIR.mkdir(exist_ok=True)


def save_experiment(ax_client: _AxClient) -> Dict:
    """Save experiment to a JSON file."""
    experiment_id = str(uuid4())
    file_path = EXPERIMENT_DIR / f"{experiment_id}.json"
    with open(file_path, "w") as f:
        json.dump(ax_client.to_json_snapshot(), f)
    return {"experiment_id": experiment_id}


def update_experiment(experiment_id: str, ax_client: _AxClient) -> None:
    """Update experiment with new data."""
    file_path = EXPERIMENT_DIR / f"{experiment_id}.json"
    with open(file_path, "w") as f:
        json.dump(ax_client.to_json_snapshot(), f)


def load_experiment(experiment_id: str) -> _AxClient:
    """Load experiment from a JSON file."""
    file_path = EXPERIMENT_DIR / f"{experiment_id}.json"
    with open(file_path, "r") as f:
        ax_client_snapshot = json.load(f)
    return _AxClient().from_json_snapshot(ax_client_snapshot)


def list_experiments() -> Dict:
    """List all experiments."""
    experiments = [
        {"experiment_id": file.stem} for file in EXPERIMENT_DIR.glob("*.json")
    ]
    return {"experiments": experiments}
