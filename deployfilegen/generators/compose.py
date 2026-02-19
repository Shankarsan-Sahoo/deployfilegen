def generate_docker_compose(mode: str, config: dict, with_db: bool = False) -> str:
    """
    Generates docker-compose.yml for production or dev.
    """
    backend_image = config["BACKEND_IMAGE_NAME"]
    frontend_image = config["FRONTEND_IMAGE_NAME"]
    
    if mode == "dev":
        return _generate_dev_compose(backend_image, frontend_image, with_db)
    else:
        return _generate_prod_compose(backend_image, frontend_image, with_db)

def _generate_prod_compose(backend_image: str, frontend_image: str, with_db: bool) -> str:
    db_service = ""
    db_depends = ""
    if with_db:
        db_service = """
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-appdb}
      - POSTGRES_USER=${POSTGRES_USER:-appuser}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-appuser} -d ${POSTGRES_DB:-appdb}"]
      interval: 10s
      timeout: 5s
      retries: 5
"""
        db_depends = """
    depends_on:
      db:
        condition: service_healthy"""

    return f"""version: '3.8'

services:
  backend:
    image: ${BACKEND_IMAGE_NAME}:${IMAGE_TAG:-latest}
    
    restart: always{db_depends}
    environment:
      - DJANGO_SECRET_KEY=${{DJANGO_SECRET_KEY}}
      - DATABASE_URL=${{DATABASE_URL}}
      - DEBUG=${{DEBUG:-False}}
      - POSTGRES_DB=${{POSTGRES_DB:-appdb}}
      - POSTGRES_USER=${{POSTGRES_USER:-appuser}}
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD}}
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    # deploy:
    #   resources:
    #     limits:
    #       cpus: '0.50'
    #       memory: 512M
    #     reservations:
    #       cpus: '0.25'
    #       memory: 256M
{db_service}
  frontend:
    image: ${FRONTEND_IMAGE_NAME}:${IMAGE_TAG:-latest}
    
    restart: always
    ports:
      - "80:8080"
    depends_on:
      backend:
        condition: service_healthy
    # deploy:
    #   resources:
    #     limits:
    #       cpus: '0.50'
    #       memory: 512M
    #     reservations:
    #       cpus: '0.25'
    #       memory: 256M

volumes:
  static_volume:
  media_volume:{"\n  postgres_data:" if with_db else ""}
"""

def _generate_dev_compose(backend_image: str, frontend_image: str, with_db: bool) -> str:
    db_service = ""
    if with_db:
        db_service = """
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
"""
    return f"""version: '3.8'

services:
  backend:
    build:
      context: ./backend
    environment:
      - DJANGO_SECRET_KEY=${{DJANGO_SECRET_KEY}}
      - DATABASE_URL=${{DATABASE_URL}}
      - DEBUG=${{DEBUG:-True}}
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
{db_service}
  frontend:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    stdin_open: true
    tty: true
"""
