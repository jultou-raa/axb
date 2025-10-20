# RESTful API for ax-platform Service

## Overview

This project aims to construct a RESTful API that sits atop Meta's ax-platform
service API, enhancing its accessibility and integration capabilities.

## Key Features

- Exposes ax-platform functionality through a user-friendly REST API.
- Simplifies interaction with ax-platform services for external applications.
- Fosters seamless integration with diverse systems and workflows.

## Technologies Used

- Python
- FastAPI
- ax-platform
- Hatch (project and environment management via pyproject.toml)

## Starting the server and accessing API documentation

This project uses pyproject.toml and Hatch (hatch) for environment and dependency management.

1. Install Hatch
   - Recommended (isolated): using pipx
     ```bash
     pipx install hatch
     ```
   - Or with pip:
     ```bash
     pip install hatch
     ```

2. Create the project environment and install dependencies
   - Create the environment defined in pyproject.toml:
     ```bash
     hatch env create
     ```
   - Alternatively, run commands inside the project environment without first creating it explicitly using:
     ```bash
     hatch run <command>
     ```

3. Start the server
   - Run the FastAPI app inside the hatch environment:
     ```bash
     hatch run uvicorn axb.api:app --reload --host 0.0.0.0 --port 8000
     ```
     or
     ```bash
     hatch run python -m uvicorn axb.api:app --reload --host 0.0.0.0 --port 8000
     ```
   - The FastAPI application is defined in the `axb.api` module (app variable).

4. Open the API documentation
   - Swagger UI (interactive): http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

5. Quick sanity checks / usage examples
   - Health / version endpoint:
     ```bash
     hatch run curl http://127.0.0.1:8000/
     ```
   - Example endpoints (use JSON bodies as shown in the `axb/tests` folder):
     - POST /create
     - POST /next
     - POST /register
     - POST /status

6. Running tests
   - Run tests inside the hatch environment:
     ```bash
     hatch run pytest -q
     ```
   - If a separate test environment is defined in pyproject.toml, create it first:
     ```bash
     hatch env create <env-name>
     hatch run -e <env-name> pytest -q
     ```

Notes:
- If you run into import issues when starting the server, ensure your current working directory is the project root so Python can import the `axb` package (or set PYTHONPATH accordingly).
- Replace host/port values as needed for deployment environments.
- See pyproject.toml for the list of dependencies and any environment-specific configuration.

## Contributing

- Contributions are warmly welcomed!
- Please refer to the CONTRIBUTING.md file for guidelines.

## License

- This project is licensed under the MIT License.

## Citation

- Meta AI. (2023). ax-platform Service API. Retrieved from
  [https://ax.dev/](https://ax.dev/)

## Disclaimer

- This project is not affiliated with or endorsed by Meta in any way.
