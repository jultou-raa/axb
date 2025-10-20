# Ax-platform Bayesian Hyperparameter Optimization API

This document provides a comprehensive guide to using the Ax-platform Bayesian Hyperparameter Optimization API. We will use the Hartmann 6 problem as a running example to illustrate the API's functionality.

## Introduction

The Ax-platform is a powerful tool for optimizing experiments, and this API provides a convenient RESTful interface to its core features. The API is stateless, meaning that the client is responsible for managing the state of the experiment. This is achieved by passing a JSON snapshot of the experiment state back and forth between the client and the server.

## The Hartmann 6 Problem

The Hartmann 6 problem is a standard benchmark problem for optimization algorithms. It is a 6-dimensional function with a single global minimum. The goal is to find the set of parameters that minimizes the function.

## API Usage

The API provides the following endpoints:

- `POST /create`: Creates a new experiment.
- `POST /next`: Generates the next trial to be evaluated.
- `POST /register`: Registers the results of a completed trial.
- `POST /status`: Retrieves the current status of the experiment.
- `POST /save`: Saves the current state of the experiment to a JSON file.

### Step 1: Create an Experiment

To start an optimization, you first need to create an experiment. This is done by sending a `POST` request to the `/create` endpoint with a JSON payload that defines the experiment.

The payload should have the following structure:

```json
{
  "experiment": {
    "name": "hartmann_test_problem",
    "parameters": [
      {
        "name": "x1",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      },
      {
        "name": "x2",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      },
      {
        "name": "x3",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      },
      {
        "name": "x4",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      },
      {
        "name": "x5",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      },
      {
        "name": "x6",
        "type": "range",
        "bounds": [0.0, 1.0],
        "value_type": "float"
      }
    ],
    "objectives": {
      "hartmann6": "minimize"
    },
    "parameter_constraints": [],
    "outcome_constraints": []
  }
}
```

Here's an example of how to create an experiment using `curl`:

```bash
curl -X POST http://localhost:8000/create -H "Content-Type: application/json" -d '{
  "experiment": {
    "name": "hartmann_test_problem",
    "parameters": [
      {"name": "x1", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
      {"name": "x2", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
      {"name": "x3", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
      {"name": "x4", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
      {"name": "x5", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
      {"name": "x6", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"}
    ],
    "objectives": {
      "hartmann6": "minimize"
    },
    "parameter_constraints": [],
    "outcome_constraints": []
  }
}'
```

The server will respond with a JSON snapshot of the newly created experiment. This snapshot should be saved by the client, as it will be needed for subsequent API calls.

### Step 2: Get the Next Trial

Once the experiment is created, you can get the next trial to be evaluated by sending a `POST` request to the `/next` endpoint. The request body should contain the JSON snapshot of the experiment that you received in the previous step.

Here's an example of how to get the next trial using `curl`:

```bash
curl -X POST http://localhost:8000/next -H "Content-Type: application/json" -d 'YOUR_EXPERIMENT_SNAPSHOT'
```

Replace `YOUR_EXPERIMENT_SNAPSHOT` with the JSON snapshot you received from the `/create` endpoint.

The server will respond with the parameters for the next trial, as well as an updated experiment snapshot.

### Step 3: Evaluate the Trial and Register the Results

After you have evaluated the trial, you need to register the results with the server. This is done by sending a `POST` request to the `/register` endpoint. The request body should contain the updated experiment snapshot, the trial ID, and the results of the evaluation.

The results should be in the following format:

```json
{
  "ax_client": YOUR_UPDATED_EXPERIMENT_SNAPSHOT,
  "trial_ids": [TRIAL_ID],
  "trial_values": [
    {
      "hartmann6": [OBJECTIVE_VALUE, STANDARD_ERROR]
    }
  ]
}
```

Replace `YOUR_UPDATED_EXPERIMENT_SNAPSHOT` with the snapshot you received from the `/next` endpoint, `TRIAL_ID` with the ID of the trial you just evaluated, `OBJECTIVE_VALUE` with the value of the objective function for the trial, and `STANDARD_ERROR` with the standard error of the measurement.

Here's an example of how to register the results using `curl`:

```bash
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{
  "ax_client": YOUR_UPDATED_EXPERIMENT_SNAPSHOT,
  "trial_ids": [0],
  "trial_values": [
    {
      "hartmann6": [-3.32237, 0.0]
    }
  ]
}'
```

The server will respond with a final updated experiment snapshot.

### Step 4: Repeat

Repeat steps 2 and 3 for as many trials as you want to run. With each iteration, the Ax-platform will use the results of the previous trials to suggest better parameters for the next trial.

### Step 5: Get the Experiment Status

At any point, you can get the current status of the experiment by sending a `POST` request to the `/status` endpoint. The request body should contain the latest experiment snapshot.

```bash
curl -X POST http://localhost:8000/status -H "Content-Type: application/json" -d 'YOUR_LATEST_EXPERIMENT_SNAPSHOT'
```

The server will respond with a summary of the experiment, including the best parameters found so far.

### Step 6: Save the Experiment

You can save the state of the experiment to a file at any time by sending a `POST` request to the `/save` endpoint. The request body should contain the latest experiment snapshot.

```bash
curl -X POST http://localhost:8000/save -H "Content-Type: application/json" -d 'YOUR_LATEST_EXPERIMENT_SNAPSHOT' > hartmann_experiment.json
```

This will save the experiment to a file named `hartmann_experiment.json`. You can later use the contents of this file to resume the experiment.
