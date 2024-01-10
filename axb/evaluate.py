from pydantic import BaseModel
from ax.core import types

class AxTrialResults(BaseModel):
    ax_client: dict
    trial_ids: list[int]
    trial_values: list[dict[str, tuple[float, float]]]