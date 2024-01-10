from pathlib import Path
from fastapi.testclient import TestClient
from axb.api import app
from axb.tests.utils import load_json
from ax.utils.measurement.synthetic_functions import hartmann6
import numpy
import pandas
test_client = TestClient(app)

def test_hartmann6_optim():
    """HARTMANN 6-DIMENSIONAL minimum finding test.
    https://www.sfu.ca/~ssurjano/hart6.html
    """

    # Initialize problem
    hartmann6_json = load_json(Path(__file__).parent / "create" / "create_hartmann.json")

    # Create client and setup experiment using json data
    response = test_client.post("/create", json=hartmann6_json)
    serialized_ax_client = response.json()
    # Define how to evaluate trials (can be replaced with external system)
    def evaluate(parameters):
        x = numpy.array([parameters.get(f"x{i+1}") for i in range(6)])
        return {
            "hartmann6": (hartmann6(x), 0.0),
            "l2norm": (numpy.sqrt((x**2).sum()), 0.0)
        }

    # Run optimization loop
    for i in range(25):
        response = test_client.post("/next", json=serialized_ax_client)
        serialized_ax_client = response.json()['ax_client']
        for trial in response.json()["trial_to_run"]:
            trial_id, parameters = trial.values()
            values = evaluate(parameters)
            body = {"ax_client":serialized_ax_client} | {"trial_ids": [trial_id], "trial_values": [values]}
            response = test_client.post("register", json=body)
            serialized_ax_client = response.json()['ax_client']

    # Everything as be done properly
    status = test_client.post("/status", json=serialized_ax_client)
    assert status.status_code == 200

    parameters = status.json()['current_estimated_optimal_parameters']

    print("Best parameters :", parameters)
    print("Hartmann6 value is", evaluate(parameters))

    print("Best known value is", hartmann6.fmin)
    
if __name__ == "__main__":
    test_hartmann6_optim()