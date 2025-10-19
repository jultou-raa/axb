from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from io import BytesIO
from fastapi.responses import StreamingResponse
from ax.generation_strategy.dispatch_utils import choose_generation_strategy_legacy
from ax.service.ax_client import ObjectiveProperties
from axb.axclient import _AxClient
from ax.version import version as ax_version
from axb._version import __version__
from axb.models import AxConfig, AxTrialResults, NextTrialResponse, RegisterTrialResponse
from axb.create import create_client_from_json
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


def transition_index(axclient: _AxClient):
    model_transition = axclient.generation_strategy.model_transitions
    return model_transition[0] if len(model_transition) > 0 else 1


@app.get("/")
def home():
    return {"api_version": __version__, "ax_version": ax_version}


def get_generation_strategy(ax_config: AxConfig):
    if ax_config.generation_strategy:
        return choose_generation_strategy_legacy(
            search_space=ax_config.experiment.parameters,
            generation_strategy_kwargs={"steps": ax_config.generation_strategy},
        )
    return None


@app.post("/create")
def read_root(ax_config: AxConfig):
    generation_strategy = get_generation_strategy(ax_config)
    client = _AxClient(generation_strategy=generation_strategy, verbose_logging=False)

    # Update objective dict
    target = {
        "minimize": ObjectiveProperties(minimize=True),
        "maximize": ObjectiveProperties(minimize=False),
    }

    objectives = {
        k: target[v] for k, v in ax_config.experiment.objectives.items()
    }

    client.create_experiment(
        parameters=ax_config.experiment.parameters,
        name=ax_config.experiment.name,
        parameter_constraints=ax_config.experiment.parameter_constraints,
        outcome_constraints=ax_config.experiment.outcome_constraints,
        objectives=objectives,
    )
    return client.to_json_snapshot()


@app.post("/next", response_model=NextTrialResponse)
def generate_trial(ax_json: dict, batch_size: int = 1):
    ax_client = create_client_from_json(ax_json)
    trial_to_run, optim_complete = ax_client.get_next_trials(batch_size)
    return {
        "trial_to_run": [
            {"id": trial_id, "parameters": trial}
            for trial_id, trial in trial_to_run.items()
        ],
        "ax_client": ax_client.to_json_snapshot(),
    }


@app.post("/register", response_model=RegisterTrialResponse)
def register_trial_value(record: AxTrialResults):
    ax_json = record.ax_client
    trial_ids = record.trial_ids
    trial_values = record.trial_values
    ax_client = create_client_from_json(ax_json)
    for trial_id, trial_value in zip(trial_ids, trial_values):
        ax_client.complete_trial(trial_id, trial_value)  # type: ignore
    return {
        "ax_client": ax_client.to_json_snapshot(),
    }


@app.post("/status")
def get_model_status(ax_json: dict):
    ax_client = create_client_from_json(ax_json)
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
async def save_model(ax_json: dict):
    # Convert JSON string to bytes object
    ax_client = create_client_from_json(ax_json)
    json_bytes = BytesIO(json.dumps(ax_client.to_json_snapshot()).encode())
    filename = f"{ax_client.experiment.name}_model.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([json_bytes.getvalue()]), headers=headers)

# TODO: Special cases https://ax.dev/tutorials/gpei_hartmann_service.html#Special-Cases
# - [] Evaluation failure
# - [] Custom trial