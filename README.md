# store-service

Flask-based microservice for managing store data in an e-commerce platform.

## Features

- Create, update, fetch, list, and delete stores.
- JWT-protected endpoints for write operations.
- Session validation via Redis token cache.
- OpenAPI docs via Flask-Smorest Swagger UI.
- Unit test suite with pytest and pytest-cov.

## Tech Stack

- Python 3.12+
- Flask
- Flask-Smorest
- Flask-SQLAlchemy
- MySQL (via PyMySQL)
- Redis
- Pytest + pytest-cov

## Project Structure

```text
.
|-- .github/
|   `-- workflows/
|       `-- store-build.yaml
|-- infra/
|-- K8s/
|-- src/
|   `-- store_service/
|       |-- main.py
|       |-- extensions/
|       |   |-- db.py
|       |   `-- redis_client.py
|       |-- helper/
|       |   `-- edifact_parser.py
|       |-- models/
|       |   `-- store_db.py
|       |-- resources/
|       |   `-- store.py
|       |-- schemas/
|       |   `-- store_schema.py
|       `-- utils/
|           `-- edifact_transformer.py
|-- tests/
|   |-- conftest.py
|   `-- unit/
|       |-- app/
|       |-- extensions/
|       |-- helper/
|       |-- resources/
|       |-- schemas/
|       `-- utils/
|-- Dockerfile
|-- Dockerfile.prod
|-- pyproject.toml
|-- requirements.txt
`-- run.py
```

## Setup

### 1. Create and activate virtual environment

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the repository root.

Required:

```env
MYSQL_USER=store_user
MYSQL_PASSWORD=store_pass
MYSQL_DATABASE=store_db
DB_HOST=localhost
DB_PORT=3306

JWT_SECRET_KEY=your_jwt_secret
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

Notes:

- `ALLOWED_ORIGINS` must be set (comma-separated values), because the app parses it directly.
- The app currently builds DB URI from environment and initializes tables at startup.

## Run the Service

```bash
python run.py
```

Default URLs:

- Health: `http://localhost:5000/health`
- Swagger UI: `http://localhost:5000/swagger-ui`

## API Endpoints

Base routes are defined in `store_service.resources.store`.

- `GET /store/<store_id>`: Get one store.
- `DELETE /store/<store_id>`: Delete store (JWT required).
- `PUT /store/<store_id>`: Update store (JWT required).
- `GET /stores`: List stores for current user (JWT required).
- `POST /create_store`: Create a store (JWT required).

## Testing and Coverage

Run tests:

```bash
pytest
```

Coverage is configured in `pyproject.toml`:

- source: `src/store_service`
- fail-under: `85`
- reports:
	- terminal missing lines
	- `coverage.xml`
	- `htmlcov/`

Open HTML coverage report:

- File: `htmlcov/index.html`

## CI/CD

Workflow file: `.github/workflows/store-build.yaml`

- Runs SAST using reusable workflow.
- Runs build/test using reusable workflow.
- Uses inherited secrets from caller repository.

## Docker

The repository includes:

- `Dockerfile`
- `Dockerfile.prod`

Use the file aligned to your deployment target (development or production image build).

## License

See `LICENSE`.
