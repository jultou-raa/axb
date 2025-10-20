"""
This module provides a custom AxClient class, `_AxClient`, which extends the functionality
of the base `AxClient` for this specific application.
"""
from ax.service.ax_client import AxClient


class _AxClient(AxClient):
    """
    A custom AxClient that provides additional properties for easier access to
    experiment information.
    """

    @property
    def transition_index(self):
        """
        Returns the index of the first model transition in the generation strategy.
        """
        model_transitions = self.generation_strategy.model_transitions
        return model_transitions[0] if model_transitions else 1

    @property
    def completed_trials(self):
        """
        Fetches the results of all completed trials in the experiment.
        """
        return self.experiment.fetch_data_results()
