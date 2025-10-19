from ax.service.ax_client import AxClient

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
        return self.experiment.fetch_data().df
