# deployfilegen

**deployfilegen** is a production-grade Python CLI library designed to automatically generate infrastructure-as-code for full-stack applications (Django + React/Next.js/Vite).

It automates the creation of **Dockerfiles**, **docker-compose.yml**, and **GitHub Actions** workflows, using secure, battle-tested defaults.

## 🚀 Key Features (v0.1.31+)

- **Zero-Config Dev Mode**: Works with *any* existing `.env` file. No forced variable naming.
- **Smart Framework Detection**: Automatically detects **Vite** (port 5173), **Next.js** (port 3000), or **Create React App**.
- **Flexible Deployment**: Choose between **SSH Build** (default) or **Registry Push** strategies.
- **Production-Grade Defaults**:
    - **Security**: Non-root users, unprivileged Nginx.
    - **Reliability**: Healthchecks, restart policies, race-condition prevention.
    - **Optimization**: Multi-stage builds, `.dockerignore` generation, layer caching.

---

## 📦 Quick Start

### 1. Install
```bash
pip install deployfilegen
```

### 2. Local Development (Zero Config)
```bash
# Generate dev config (auto-detects your stack)
deployfilegen init --mode dev

# Start your app
docker compose -f docker-compose.dev.yml up --build

# With a Postgres database
deployfilegen init --mode dev --with-db --force
docker compose -f docker-compose.dev.yml up --build
```

### 3. Production — SSH Build (Default, Recommended)
Build images directly on your server. **No container registry needed.**

```bash
# Generate production config
deployfilegen init --mode prod --deploy ssh

# Or just (ssh is the default):
deployfilegen init --mode prod
```

**Required `.env` variables (only 2!):**
```ini
DEPLOY_HOST=your_server_ip
DEPLOY_USER=ubuntu
```

**Generated GitHub Actions workflow will:**
```
SSH into server → git pull → docker compose build → docker compose up -d
```

### 4. Production — Registry Push (Advanced)
Push images to Docker Hub/GHCR, then pull on server. Use this for immutable deployments.

```bash
deployfilegen init --mode prod --deploy registry
```

**Required `.env` variables:**
```ini
# Server (always required)
DEPLOY_HOST=your_server_ip
DEPLOY_USER=ubuntu

# Registry (only required for --deploy registry)
DOCKER_USERNAME=your_username
BACKEND_IMAGE_NAME=user/backend
FRONTEND_IMAGE_NAME=user/frontend
```

**Generated GitHub Actions workflow will:**
```
Build images → Push to Registry → SSH into server → docker compose pull → up -d
```

---

## 🛠 Supported Stacks

| Component | Framework | Auto-Detected |
|:---|:---|:---|
| **Backend** | Django | Project name from `manage.py` |
| **Frontend** | Vite | Port `5173`, `--host` binding |
| **Frontend** | Next.js | Port `3000`, `-H` binding |
| **Frontend** | CRA | Port `3000`, `HOST` env |

---

## ⚙️ Configuration

Generate a boilerplate `.env` with the right variables for your strategy:
```bash
# SSH mode (minimal — just 2 vars)
deployfilegen template

# Registry mode (includes image names)
deployfilegen template --deploy registry
```

---

## 📖 CLI Reference

```text
Usage: deployfilegen init [OPTIONS]

Options:
  --mode [dev|prod]       Generation mode (Default: prod)
  --deploy [ssh|registry] Deployment strategy (Default: ssh)
  --force, -f             Overwrite existing files
  --with-db               Include a Postgres service in docker-compose

  # Scope Control
  --docker-only           Generate only Dockerfiles
  --compose-only          Generate only docker-compose.yml
  --github-only           Generate only GitHub Actions (Prod only)
  --backend-only          Only generate backend assets
  --frontend-only         Only generate frontend assets

  # Override Detection
  --frontend-port INT     Override detected frontend dev port
  --start-command TEXT    Override detected frontend start command
  --project-name TEXT     Override detected Django project name

  --help                  Show this message
```

---

## 🔧 Troubleshooting

**"Missing required variables" error in prod mode?**
```bash
# Check which variables you need:
deployfilegen template              # SSH: just DEPLOY_HOST + DEPLOY_USER
deployfilegen template --deploy registry  # Registry: adds DOCKER_USERNAME + IMAGE_NAMEs
```

**Frontend container exits immediately?**
Your dev server might not be binding to `0.0.0.0`. Override the start command:
```bash
deployfilegen init --mode dev --start-command "serve" --force
```

**Wrong port detected?**
```bash
deployfilegen init --mode dev --frontend-port 8080 --force
```

**Django project name wrong?**
```bash
deployfilegen init --mode prod --project-name my_project --force
```

---

## 📄 License
MIT
