from ax.service.ax_client import AxClient
from ax.generation_strategy.generation_node import GenerationStep
from ax.core.observation import ObservationFeatures
from ax.api.utils.generation_strategy_dispatch import choose_generation_strategy
from ax.generators.torch.botorch_modular.generator import BoTorchGenerator
import torch
from botorch.models.gp_regression import SingleTaskGP
from botorch.acquisition import qUpperConfidenceBound

class _AxClient(AxClient):
    @property
    def transition_index(self):
        model_transition = self.generation_strategy.model_transitions
        return model_transition[0] if len(model_transition) > 0 else 1

    @property
    def direction_translation(self):
        return {True: "minimiser", False: "maximiser", None: "non définit"}

    @property
    def completed_trials(self):
        return self.experiment.fetch_data_results()
