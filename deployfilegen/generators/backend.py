import re
from pathlib import Path
from deployfilegen.utils.logger import logger

def get_django_project_name(manage_py_path: Path) -> str:
    """
    Parses manage.py to find the Django project name from DJANGO_SETTINGS_MODULE.
    Defaults to 'config' if not found.
    """
    try:
        content = manage_py_path.read_text(encoding="utf-8")
        match = re.search(r"os\.environ\.setdefault\(['\"]DJANGO_SETTINGS_MODULE['\"],\s*['\"](.+?)\.settings['\"]\)", content)
        if match:
            project_name = match.group(1)
            logger.info(f"Detected Django project name: {project_name}")
            return project_name
    except Exception as e:
        logger.warning(f"Failed to parse manage.py: {e}")
    
    logger.warning("Could not detect Django project name. Defaulting to 'config'.")
    return "config"

def generate_backend_dockerfile(mode: str, backend_path: Path) -> str:
    """
    Generates a production-ready or dev Dockerfile for Django.
    """
    if mode == "dev":
        return _generate_dev_dockerfile()
    else:
        project_name = get_django_project_name(backend_path / "manage.py")
        return _generate_prod_dockerfile(project_name)

def _generate_prod_dockerfile(project_name: str) -> str:
    return f"""# Production Dockerfile for Django

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev curl \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Collect static files (ensure this is safe to run without DB connection if needed)
# Or handle this in entrypoint on deployment.
RUN DJANGO_SECRET_KEY=build-time-dummy DATABASE_URL=sqlite:///db.sqlite3 python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run gunicorn
CMD ["gunicorn", "{project_name}.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
"""

def _generate_dev_dockerfile() -> str:
    return """# Development Dockerfile for Django
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""
