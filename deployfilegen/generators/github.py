def generate_github_workflow(config: dict) -> str:
    """
    Generates a production GitHub Actions workflow.
    """
    docker_username = config["DOCKER_USERNAME"]
    backend_image = config["BACKEND_IMAGE_NAME"]
    frontend_image = config["FRONTEND_IMAGE_NAME"]
    deploy_host = config["DEPLOY_HOST"]
    deploy_user = config["DEPLOY_USER"]
    
    return f"""name: Deploy to Production

on:
  push:
    branches: [ "main" ]

concurrency:
  group: production
  cancel-in-progress: false

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4  # v4.1.1 (pinning recommended)

    - name: Set up QEMU
      uses: docker/setup-qemu-action@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        registry: docker.io
        username: ${{{{ secrets.DOCKER_USERNAME }}}}
        password: ${{{{ secrets.DOCKERHUB_TOKEN }}}}

    - name: Build and Push Backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: |
          {backend_image}:latest
          {backend_image}:${{{{ github.sha }}}}
        cache-from: type=registry,ref={backend_image}:buildcache
        cache-to: type=registry,ref={backend_image}:buildcache,mode=max

    - name: Build and Push Frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: |
          {frontend_image}:latest
          {frontend_image}:${{{{ github.sha }}}}
        cache-from: type=registry,ref={frontend_image}:buildcache
        cache-to: type=registry,ref={frontend_image}:buildcache,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@e5bb55e85072516e05f153bd69632a2656345fa4 # v1.0.0 (pinned)
      with:
        host: ${{{{ secrets.DEPLOY_HOST }}}}
        username: ${{{{ secrets.DEPLOY_USER }}}}
        key: ${{{{ secrets.SSH_PRIVATE_KEY }}}}
        script: |
          cd /path/to/project
          export COMPOSE_PROJECT_NAME=production
          export IMAGE_TAG=${{{{ github.sha }}}}
          docker compose -f docker-compose.prod.yml pull
          docker compose -f docker-compose.prod.yml up -d --remove-orphans
"""
