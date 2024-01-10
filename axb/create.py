from pydantic import BaseModel
from axb.axclient import _AxClient

class Experiment(BaseModel):
    name: str
    parameters: list[dict]
    objectives: dict
    parameter_constraints: list[str]
    outcome_constraints: list[str]

class AxConfig(BaseModel):
    experiment: Experiment

def create_client_from_json(ax_json):
    return _AxClient().from_json_snapshot(ax_json)