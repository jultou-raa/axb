from fastapi.testclient import TestClient
from axb.api import app
from axb.tests.utils import load_json
import json
import pathlib
import pytest

test_client = TestClient(app)

create_json_files = (pathlib.Path(__file__).parent / "create").rglob("*.json")
generate_json_files = (pathlib.Path(__file__).parent / "generate").rglob("*.json")
status_json_files = (pathlib.Path(__file__).parent / "status").rglob("*.json")
register_json_files = (pathlib.Path(__file__).parent / "register").rglob("*.json")


def test_home():
    assert test_client.get("/").status_code == 200


@pytest.mark.parametrize("file_path", create_json_files)
def test_create(file_path):
    json_data = load_json(file_path)
    assert test_client.post("/create", json=json_data).status_code == 200


@pytest.mark.parametrize("file_path", generate_json_files)
def test_generate_trial(file_path):
    json_data = load_json(file_path)
    assert test_client.post("/next", json=json_data).status_code == 200


@pytest.mark.parametrize("file_path", status_json_files)
def test_status(file_path):
    json_data = load_json(file_path)
    assert test_client.post("/status", json=json_data).status_code == 200

@pytest.mark.parametrize("file_path", register_json_files)
def test_register(file_path):
    json_data = load_json(file_path)
    assert test_client.post("/register", json=json_data).status_code == 200