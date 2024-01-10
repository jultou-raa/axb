from ax.service.ax_client import AxClient
from ax.modelbridge.registry import Models
from ax.models.torch.botorch_modular.surrogate import Surrogate
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

    def get_best_parameters_from_model(self):

        gp_posterior_mean = Models.BOTORCH_MODULAR(
            experiment=self.experiment,
            data=self.experiment.fetch_data(),
            surrogate=Surrogate(SingleTaskGP),
            botorch_acqf_class=qUpperConfidenceBound,
        )
        trial = gp_posterior_mean.gen(1)
        return trial.arms[0].parameters