"""
This module defines the API endpoints for the Ax-platform hyperparameter optimization service.
It provides a RESTful interface to create, manage, and interact with Ax experiments.
"""

import json
import logging
from io import BytesIO

from ax.service.ax_client import ObjectiveProperties
from ax.version import version as ax_version
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from axb._version import __version__
from axb.axclient import _AxClient
from axb.create import AxConfig, create_client_from_json
from axb.evaluate import AxTrialResults

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(version=__version__)


@app.get("/")
def home():
    """
    Returns the version of the API and the underlying Ax-platform.
    """
    return {"api_version": __version__, "ax_version": ax_version}


@app.post("/create")
def create_experiment(ax_config: AxConfig):
    """
    Creates a new Ax experiment based on the provided configuration.
    """
    try:
        client = _AxClient(verbose_logging=False)

        # Map objective strings to Ax ObjectiveProperties
        objective_mapping = {
            "minimize": ObjectiveProperties(minimize=True),
            "maximize": ObjectiveProperties(minimize=False),
        }

        objectives = {
            name: objective_mapping[direction]
            for name, direction in ax_config.experiment.objectives.items()
        }

        client.create_experiment(
            parameters=ax_config.experiment.parameters,
            name=ax_config.experiment.name,
            parameter_constraints=ax_config.experiment.parameter_constraints,
            outcome_constraints=ax_config.experiment.outcome_constraints,
            objectives=objectives,
        )
        logger.info(f"Successfully created experiment '{ax_config.experiment.name}'.")
        return client.to_json_snapshot()
    except Exception as e:
        logger.error(f"Error creating experiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create experiment.")


@app.post("/next")
def get_next_trial(ax_json: dict, batch_size: int = 1):
    """
    Generates the next trial(s) to be evaluated.
    """
    try:
        ax_client = create_client_from_json(ax_json)
        trial_to_run, optim_complete = ax_client.get_next_trials(batch_size)
        return {
            "trial_to_run": [
                {"id": trial_id, "parameters": trial}
                for trial_id, trial in trial_to_run.items()
            ],
            "ax_client": ax_client.to_json_snapshot(),
        }
    except Exception as e:
        logger.error(f"Error generating next trial: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate next trial.")


@app.post("/register")
def register_trial_results(record: AxTrialResults):
    """
    Registers the results of a completed trial.
    """
    try:
        ax_client = create_client_from_json(record.ax_client)
        for trial_id, trial_value in zip(record.trial_ids, record.trial_values):
            ax_client.complete_trial(trial_index=trial_id, raw_data=trial_value)
        return {
            "ax_client": ax_client.to_json_snapshot(),
        }
    except Exception as e:
        logger.error(f"Error registering trial results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to register trial results."
        )


@app.post("/status")
def get_experiment_status(ax_json: dict):
    """
    Retrieves the current status of the experiment, including the best parameters found so far.
    """
    try:
        ax_client = create_client_from_json(ax_json)
        if not ax_client.experiment.trials:
            return {"status": "No trials have been run yet."}

        optim_info = {
            "current_measured_optimal_parameters": ax_client.get_best_parameters(),
            "current_estimated_optimal_parameters": ax_client.get_best_parameters(),
        }

        return {
            "trials_data": ax_client.get_trials_data_frame()
            .replace({float("nan"): None})
            .to_dict("records"),
        } | optim_info
    except Exception as e:
        logger.error(f"Error getting experiment status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to get experiment status."
        )


@app.post("/save")
async def save_experiment_snapshot(ax_json: dict):
    """
    Saves the current state of the experiment to a JSON file.
    """
    try:
        ax_client = create_client_from_json(ax_json)
        json_bytes = json.dumps(ax_client.to_json_snapshot()).encode("utf-8")
        filename = f"{ax_client.experiment.name}_model.json"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(BytesIO(json_bytes), headers=headers)
    except Exception as e:
        logger.error(f"Error saving experiment snapshot: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to save experiment snapshot."
        )

