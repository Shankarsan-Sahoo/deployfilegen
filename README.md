# deployfilegen

**deployfilegen** is a production-grade Python CLI library designed to automatically generate production-ready deployment configuration files for full-stack applications (Django + React).

Writing Dockerfiles, Compose configs, and CI pipelines repeatedly is slow and error-prone. **deployfilegen** automates this process using secure, battle-tested defaults.

## Quick Start

```bash
# 1. Install the tool
pip install deployfilegen

# 2. Initialize your project
deployfilegen init

# 3. Deploy locally
docker compose -f docker-compose.prod.yml up --build
```

---

## Why deployfilegen?

Standardizing deployment is hard. This tool ensures your project follows industry best practices out of the box:
- **Security**: All containers run as non-root users.
- **Reliability**: Automated healthchecks and dependency waiting.
- **CI/CD**: Complete GitHub Actions workflow with Docker layer caching.
- **Zero Hardcoding**: All configuration is derived from your `.env` files.

---

## Example Project Structure

The tool expects a standard full-stack layout:

```text
my-cool-project/
├── backend/            # Django project
│   └── manage.py
├── frontend/           # React project
│   └── package.json
└── .env                # Required environment variables
```

---

## CLI Output Example

```text
$ deployfilegen init
INFO: Initializing deployfilegen in /path/to/project (Mode: prod)
INFO: Detected Django backend.
INFO: Detected React frontend.
INFO: Loaded environment from: .env
INFO: Generating Backend Dockerfile...
INFO: Generated backend/Dockerfile
INFO: Generating Frontend Dockerfile...
INFO: Generated frontend/Dockerfile
INFO: Generating Docker Compose...
INFO: Generated docker-compose.prod.yml
INFO: Generating GitHub Actions workflow...
INFO: Generated .github/workflows/deploy.yml
INFO: Deployment configuration generated successfully!
```

---

## Usage

Navigate to your project root and run:

```bash
# Generate a boilerplate .env template
deployfilegen template

# Initialize your project
deployfilegen init [OPTIONS]
```

### Commands

*   `init`: Initialize deployment configuration.
*   `template`: Generate a boilerplate `.env` file.

### Global Options
- `--version`, `-v`: Show the version and exit.
- `--help`: Show this message and exit.

### `init` Command Options

| Option | Description |
| :--- | :--- |
| `--mode prod` | Generates `docker-compose.prod.yml` (Default). Optimized for servers. |
| `--mode dev` | Generates `docker-compose.dev.yml`. Optimized for local coding. |
| `--force`, `-f` | Overwrite existing files. (Default: skips existing files). |
| `--docker-only` | Generate only the Dockerfiles. |
| `--compose-only` | Generate only the Docker Compose files. |
| `--github-only` | Generate only the GitHub Actions workflow. |
| `--backend-only` | Filter generation to only Backend components. |
| `--frontend-only` | Filter generation to only Frontend components. |

---

## Requirements

- Python 3.9+
- A project structure with a Django-based `backend` and a React-based `frontend`.
- A `.env` file containing: `DOCKER_USERNAME`, `BACKEND_IMAGE_NAME`, `FRONTEND_IMAGE_NAME`, `DEPLOY_HOST`, and `DEPLOY_USER`.

## Common Pitfalls

### 1. Django Healthcheck
The generated `docker-compose.yml` includes a healthcheck that pings `http://localhost:8000/health`. If this endpoint is missing, your container will be marked as "unhealthy" and may restart.

**Quick Fix**: Add this to your `urls.py`:
```python
from django.http import HttpResponse
from django.urls import path

urlpatterns = [
    path('health', lambda r: HttpResponse("OK")),
    # ... your other paths
]
```

### 2. Database Connection
Ensure your `DATABASE_URL` in `.env` uses the service name if you are using the `--with-db` flag:
`DATABASE_URL=postgres://appuser:password@db:5432/appdb`

## License

MIT
