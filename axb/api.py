from fastapi import FastAPI
from io import BytesIO
from fastapi.responses import StreamingResponse
from ax.service.ax_client import ObjectiveProperties
from axb.axclient import _AxClient
from ax.version import version as ax_version
from axb._version import __version__
from axb.create import AxConfig, create_client_from_json
from axb.evaluate import AxTrialResults
import json

app = FastAPI(version=__version__)


def transition_index(axclient: _AxClient):
    model_transition = axclient.generation_strategy.model_transitions
    return model_transition[0] if len(model_transition) > 0 else 1


@app.get("/")
def home():
    return {"api_version": __version__, "ax_version": ax_version}


@app.post("/create")
def read_root(ax_config: AxConfig):
    client = _AxClient(verbose_logging=False)

    # Update objective dict
    target = {
        "minimize": ObjectiveProperties(minimize=True),
        "maximize": ObjectiveProperties(minimize=False),
    }

    ax_config.experiment.objectives = {
        k: target[v] for k, v in ax_config.experiment.objectives.items()
    }

    client.create_experiment(
        parameters=ax_config.experiment.parameters,
        name=ax_config.experiment.name,
        parameter_constraints=ax_config.experiment.parameter_constraints,
        outcome_constraints=ax_config.experiment.outcome_constraints,
        objectives=ax_config.experiment.objectives,
    )
    return client.to_json_snapshot()


@app.post("/next")
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


@app.post("/register")
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
    if any(ax_client.completed_trials.values()):
        optim_info = {
            "current_measured_optimal_parameters": ax_client.get_best_parameters(),
            "current_estimated_optimal_parameters": ax_client.get_best_parameters_from_model(),
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