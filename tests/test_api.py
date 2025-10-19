from fastapi.testclient import TestClient
from axb.api import app
from ax.version import version as ax_version
from axb._version import __version__

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"api_version": __version__, "ax_version": ax_version}

def test_create_experiment():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    assert response.status_code == 200
    assert "experiment_id" in response.json()

def test_next_trial():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    experiment_id = response.json()["experiment_id"]
    response = client.post(f"/next?experiment_id={experiment_id}&batch_size=1")
    assert response.status_code == 200
    assert "trial_to_run" in response.json()
    assert len(response.json()["trial_to_run"]) == 1

def test_register_trial():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    experiment_id = response.json()["experiment_id"]
    response = client.post(f"/next?experiment_id={experiment_id}&batch_size=1")
    trial = response.json()["trial_to_run"][0]
    response = client.post(
        "/register",
        json={
            "experiment_id": experiment_id,
            "trial_ids": [trial["id"]],
            "trial_values": [{"branin": [0.0, 0.0]}],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_get_model_status():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    experiment_id = response.json()["experiment_id"]
    response = client.post(f"/next?experiment_id={experiment_id}&batch_size=1")
    trial = response.json()["trial_to_run"][0]
    client.post(
        "/register",
        json={
            "experiment_id": experiment_id,
            "trial_ids": [trial["id"]],
            "trial_values": [{"branin": [0.0, 0.0]}],
        },
    )
    response = client.post(f"/status?experiment_id={experiment_id}")
    assert response.status_code == 200
    assert "data" in response.json()
    assert "current_measured_optimal_parameters" in response.json()

def test_get_experiments():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    experiment_id = response.json()["experiment_id"]
    response = client.get("/experiments")
    assert response.status_code == 200
    assert any(
        exp["experiment_id"] == experiment_id
        for exp in response.json()["experiments"]
    )

def test_get_experiment():
    response = client.post(
        "/create",
        json={
            "experiment": {
                "name": "test_experiment",
                "parameters": [
                    {"name": "x", "type": "range", "bounds": [-5.0, 10.0]},
                    {"name": "y", "type": "range", "bounds": [0.0, 15.0]},
                ],
                "objectives": {"branin": "minimize"},
            }
        },
    )
    experiment_id = response.json()["experiment_id"]
    response = client.get(f"/experiments/{experiment_id}")
    assert response.status_code == 200
    assert response.json()["experiment"]["name"] == "test_experiment"
