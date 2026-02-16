def generate_docker_compose(mode: str, config: dict) -> str:
    """
    Generates docker-compose.yml for production or dev.
    """
    backend_image = config["BACKEND_IMAGE_NAME"]
    frontend_image = config["FRONTEND_IMAGE_NAME"]
    
    if mode == "dev":
        return _generate_dev_compose(backend_image, frontend_image)
    else:
        return _generate_prod_compose(backend_image, frontend_image)

def _generate_prod_compose(backend_image: str, frontend_image: str) -> str:
    return f"""version: '3.8'

services:
  backend:
    image: {backend_image}:${{IMAGE_TAG:-latest}}
    
    restart: always
    env_file:
      - .env
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

  frontend:
    image: {frontend_image}:${{IMAGE_TAG:-latest}}
    
    restart: always
    ports:
      - "80:80"
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
  media_volume:
"""

def _generate_dev_compose(backend_image: str, frontend_image: str) -> str:
    return f"""version: '3.8'

services:
  backend:
    build:
      context: ./backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app

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
