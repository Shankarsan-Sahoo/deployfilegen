def generate_github_workflow(config: dict, deploy: str = "ssh") -> str:
    """
    Generates a production GitHub Actions workflow.
    Strategy is determined by the deploy parameter:
      - 'ssh': git pull + docker compose build on server (no registry needed)
      - 'registry': build/push images + docker compose pull on server
    """
    if deploy == "registry":
        return _generate_registry_workflow(config)
    else:
        return _generate_ssh_workflow(config)


def _generate_ssh_workflow(config: dict) -> str:
    """SSH Build Mode: git pull → docker compose build → up on server."""
    return """name: Deploy to Production (SSH Build)

on:
  push:
    branches: [ "main" ]

concurrency:
  group: production
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@e5bb55e85072516e05f153bd69632a2656345fa4 # v1.0.0 (pinned)
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd ${{ secrets.DEPLOY_PATH }}
          git pull origin main
          docker compose -f docker-compose.prod.yml build
          docker compose -f docker-compose.prod.yml up -d --remove-orphans
"""


def _generate_registry_workflow(config: dict) -> str:
    """Registry Mode: build & push to registry → docker compose pull on server."""
    return """name: Deploy to Production (Registry)

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
    - uses: actions/checkout@v4

    - name: Set up QEMU
      uses: docker/setup-qemu-action@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        registry: docker.io
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and Push Backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: |
          ${{ secrets.BACKEND_IMAGE_NAME }}:latest
          ${{ secrets.BACKEND_IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.BACKEND_IMAGE_NAME }}:buildcache
        cache-to: type=registry,ref=${{ secrets.BACKEND_IMAGE_NAME }}:buildcache,mode=max

    - name: Build and Push Frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: |
          ${{ secrets.FRONTEND_IMAGE_NAME }}:latest
          ${{ secrets.FRONTEND_IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=registry,ref=${{ secrets.FRONTEND_IMAGE_NAME }}:buildcache
        cache-to: type=registry,ref=${{ secrets.FRONTEND_IMAGE_NAME }}:buildcache,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Server
      uses: appleboy/ssh-action@e5bb55e85072516e05f153bd69632a2656345fa4 # v1.0.0 (pinned)
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd ${{ secrets.DEPLOY_PATH }}
          export COMPOSE_PROJECT_NAME=production
          export BACKEND_IMAGE_NAME=${{ secrets.BACKEND_IMAGE_NAME }}
          export FRONTEND_IMAGE_NAME=${{ secrets.FRONTEND_IMAGE_NAME }}
          export IMAGE_TAG=${{ github.sha }}
          docker compose -f docker-compose.prod.yml pull
          docker compose -f docker-compose.prod.yml up -d --remove-orphans
"""
