# deployfilegen

**deployfilegen** is a production-grade Python CLI library designed to automatically generate infrastructure-as-code for full-stack applications (Django + React/Next.js/Vite).

It automates the creation of **Dockerfiles**, **docker-compose.yml**, and **GitHub Actions** workflows, using secure, battle-tested defaults.

## 🚀 Key Features (v0.1.31+)

- **Zero-Config Dev Mode**: Works with *any* existing `.env` file. No forced variable naming.
- **Smart Framework Detection**: Automatically detects **Vite** (port 5173), **Next.js** (port 3000), or **Create React App**.
- **Flexible Deployment**: Choose between **SSH Build** (default) or **Registry Push** strategies.
- **Production-Grade Defaults**:
    - **Security**: Non-root users, unprivileged Nginx.
    - **Reliability**: Healthchecks, `depends_on`, and race-condition prevention.
    - **Optimization**: Multi-stage builds, `.dockerignore` generation, layer caching.

---

## 📦 Quick Start

### 1. Install
```bash
pip install deployfilegen
```

### 2. Local Development (Zero Config)
```bash
deployfilegen init --mode dev
docker compose -f docker-compose.dev.yml up --build
```

### 3. Production — SSH Build (Default)
Build images directly on your server. No container registry needed.

```bash
deployfilegen init --mode prod --deploy ssh
```

**Required `.env` variables:**
```ini
DEPLOY_HOST=your_server_ip
DEPLOY_USER=ubuntu
```

**GitHub Actions workflow will:**
`SSH → git pull → docker compose build → docker compose up -d`

### 4. Production — Registry Push
Push images to Docker Hub/GHCR, then pull on server.

```bash
deployfilegen init --mode prod --deploy registry
```

**Required `.env` variables:**
```ini
DEPLOY_HOST=your_server_ip
DEPLOY_USER=ubuntu
DOCKER_USERNAME=your_username
BACKEND_IMAGE_NAME=user/backend
FRONTEND_IMAGE_NAME=user/frontend
```

**GitHub Actions workflow will:**
`Build → Push to Registry → SSH → docker compose pull → up -d`

---

## 🛠 Supported Stacks

**Backend:**
- **Django**: Auto-detects project name from `manage.py`.
- **Python**: Uses `3.11-slim` by default.

**Frontend:**
- **Vite**: Auto-configures port `5173` and host binding.
- **Next.js**: Auto-configures port `3000` and standalone build.
- **Create React App**: Auto-configures port `3000`.

---

## ⚙️ Configuration

Generate a boilerplate `.env`:
```bash
deployfilegen template                  # SSH mode (minimal)
deployfilegen template --deploy registry  # Registry mode (full)
```

---

## 📖 CLI Reference

```text
Usage: deployfilegen init [OPTIONS]

Options:
  --mode [dev|prod]      Generation mode (Default: prod)
  --deploy [ssh|registry] Deployment strategy (Default: ssh)
  --force, -f            Overwrite existing files
  --with-db              Include a Postgres service in docker-compose
  --docker-only          Generate only Dockerfiles
  --compose-only         Generate only docker-compose.yml
  --github-only          Generate only GitHub Actions (Prod only)
  --backend-only         Only generate backend assets
  --frontend-only        Only generate frontend assets
  # Stability Overrides
  --frontend-port        Override detected frontend dev port
  --start-command        Override detected frontend start command
  --project-name         Override detected Django project name
  --help                 Show this message
```

## 📄 License
MIT
