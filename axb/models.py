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
    experiment_id: str
    trial_ids: List[int]
    trial_values: List[Dict[str, Tuple[float, float]]]

# Response Models

class ExperimentId(BaseModel):
    experiment_id: str

class TrialToRun(BaseModel):
    id: int
    parameters: Dict[str, Any]

class NextTrialResponse(BaseModel):
    trial_to_run: List[TrialToRun]

class StatusResponse(BaseModel):
    status: str

class ExperimentDetails(BaseModel):
    name: str
    best_arm_parameters: Dict[str, Any]
    best_arm_predictions: Dict[str, Tuple[float, float]]

class ExperimentListItem(BaseModel):
    experiment_id: str

class ExperimentList(BaseModel):
    experiments: List[ExperimentListItem]
