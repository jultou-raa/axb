from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from io import BytesIO
from fastapi.responses import StreamingResponse
from ax.service.ax_client import ObjectiveProperties
from axb.axclient import _AxClient
from ax.version import version as ax_version
from axb._version import __version__
from axb.models import (
    AxConfig,
    AxTrialResults,
    ExperimentId,
    NextTrialResponse,
    StatusResponse,
    ExperimentList,
)
from axb.db import save_experiment, load_experiment, update_experiment, list_experiments
from axb.logging import setup_logging
import json
import logging

app = FastAPI(version=__version__)

setup_logging()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


@app.get("/experiments", response_model=ExperimentList)
def get_experiments():
    return list_experiments()


@app.get("/experiments/{experiment_id}", response_model=dict)
def get_experiment(experiment_id: str):
    ax_client = load_experiment(experiment_id)
    return ax_client.to_json_snapshot()


@app.get("/")
def home():
    return {"api_version": __version__, "ax_version": ax_version}


@app.post("/create", response_model=ExperimentId)
def create_experiment(ax_config: AxConfig):
    client = _AxClient(verbose_logging=False)

    # Update objective dict
    target = {
        "minimize": ObjectiveProperties(minimize=True),
        "maximize": ObjectiveProperties(minimize=False),
    }

    objectives = {
        k: target[v] for k, v in ax_config.experiment.objectives.items()
    }

    choose_gs_kwargs = None
    if ax_config.generation_strategy:
        choose_gs_kwargs = {"steps": ax_config.generation_strategy}

    client.create_experiment(
        parameters=ax_config.experiment.parameters,
        name=ax_config.experiment.name,
        parameter_constraints=ax_config.experiment.parameter_constraints,
        outcome_constraints=ax_config.experiment.outcome_constraints,
        objectives=objectives,
        choose_generation_strategy_kwargs=choose_gs_kwargs,
    )
    return save_experiment(client)


@app.post("/next", response_model=NextTrialResponse)
def generate_trial(experiment_id: str, batch_size: int = 1):
    ax_client = load_experiment(experiment_id)
    trial_to_run, optim_complete = ax_client.get_next_trials(batch_size)
    update_experiment(experiment_id, ax_client)
    return {
        "trial_to_run": [
            {"id": trial_id, "parameters": trial}
            for trial_id, trial in trial_to_run.items()
        ]
    }


@app.post("/register", response_model=StatusResponse)
def register_trial_value(record: AxTrialResults):
    ax_client = load_experiment(record.experiment_id)
    for trial_id, trial_value in zip(record.trial_ids, record.trial_values):
        ax_client.complete_trial(trial_id, trial_value)  # type: ignore
    update_experiment(record.experiment_id, ax_client)
    return {"status": "success"}


@app.post("/status")
def get_model_status(experiment_id: str):
    ax_client = load_experiment(experiment_id)
    if not ax_client.completed_trials.empty:
        optim_info = {
            "current_measured_optimal_parameters": ax_client.get_best_parameters(),
        }
    else:
        optim_info = {}
    return {
        "data": ax_client.get_trials_data_frame().fillna('N/A').to_dict(orient="records"),
    } | optim_info


@app.post("/save")
async def save_model(experiment_id: str):
    # Convert JSON string to bytes object
    ax_client = load_experiment(experiment_id)
    json_bytes = BytesIO(json.dumps(ax_client.to_json_snapshot()).encode())
    filename = f"{ax_client.experiment.name}_model.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([json_bytes.getvalue()]), headers=headers)

# TODO: Special cases https://ax.dev/tutorials/gpei_hartmann_service.html#Special-Cases
# - [] Evaluation failure
# - [] Custom trial