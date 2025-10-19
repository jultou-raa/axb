from pydantic import BaseModel
from typing import List, Dict, Tuple, Any

# Request Models

class ExperimentConfig(BaseModel):
    name: str
    parameters: List[Dict]
    objectives: Dict[str, str]
    parameter_constraints: List[str] = []
    outcome_constraints: List[str] = []

class AxConfig(BaseModel):
    experiment: ExperimentConfig
    generation_strategy: List[Dict] = []

class AxTrialResults(BaseModel):
    ax_client: dict
    trial_ids: List[int]
    trial_values: List[Dict[str, Tuple[float, float]]]

# Response Models

class TrialToRun(BaseModel):
    id: int
    parameters: Dict[str, Any]

class NextTrialResponse(BaseModel):
    trial_to_run: List[TrialToRun]
    ax_client: dict

class RegisterTrialResponse(BaseModel):
    ax_client: dict
