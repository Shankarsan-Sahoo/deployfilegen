import json
from pathlib import Path
from deployfilegen.utils.logger import logger


def detect_frontend_framework(frontend_path: Path, 
                              override_port: int = None, 
                              override_cmd: str = None) -> dict:
    """
    Detects the frontend framework from package.json with support for explicit overrides.
    Returns a dict with: framework, dev_cmd, dev_port
    """
    result = {"framework": "unknown", "dev_cmd": override_cmd or "dev", "dev_port": override_port or 3000}
    
    try:
        pkg_json = json.loads((frontend_path / "package.json").read_text(encoding="utf-8"))
        all_deps = {}
        all_deps.update(pkg_json.get("dependencies", {}))
        all_deps.update(pkg_json.get("devDependencies", {}))
        scripts = pkg_json.get("scripts", {})
        
        # Detect framework
        if "vite" in all_deps:
            result["framework"] = "vite"
            result["dev_port"] = override_port or 5173
            result["dev_cmd"] = override_cmd or "dev"
            logger.info("Detected Vite frontend framework")
        elif "next" in all_deps:
            result["framework"] = "next"
            result["dev_port"] = override_port or 3000
            result["dev_cmd"] = override_cmd or "dev"
            logger.info("Detected Next.js frontend framework")
        elif "react-scripts" in all_deps:
            result["framework"] = "cra"
            result["dev_port"] = override_port or 3000
            result["dev_cmd"] = override_cmd or "start"
            logger.info("Detected Create React App frontend framework")
        else:
            # Fallback: check scripts logic only if no override provided
            if not override_cmd:
                if "dev" in scripts:
                    result["dev_cmd"] = "dev"
                elif "start" in scripts:
                    result["dev_cmd"] = "start"

        # VALIDATION: Check if the final command exists in scripts
        # We check both the detected and the overridden command
        final_cmd = result["dev_cmd"]
        if final_cmd not in scripts:
            logger.warning(f"⚠️  Command '{final_cmd}' NOT found in package.json scripts! The container might fail to start.")
            logger.warning(f"Available scripts: {', '.join(scripts.keys())}")
                
    except Exception as e:
        logger.warning(f"Could not read package.json: {e}")
    
    return result


def generate_frontend_dockerfile(mode: str, frontend_path: Path = None, 
                                 override_port: int = None, 
                                 override_cmd: str = None) -> str:
    """
    Generates a production-ready or dev Dockerfile for React/Next.js/Vite.
    """
    framework_info = {"framework": "unknown", "dev_cmd": override_cmd or "dev", "dev_port": override_port or 3000}
    if frontend_path:
        framework_info = detect_frontend_framework(frontend_path, override_port, override_cmd)
    
    if mode == "dev":
        return _generate_dev_dockerfile(framework_info)
    else:
        return _generate_prod_dockerfile(framework_info)


def get_frontend_dev_port(frontend_path: Path = None, override_port: int = None) -> int:
    """Public helper: returns the detected dev port for use by compose generator."""
    if override_port:
        return override_port
    if frontend_path:
        info = detect_frontend_framework(frontend_path)
        return info["dev_port"]
    return 3000


def _generate_prod_dockerfile(framework_info: dict) -> str:
    # For prod, Vite outputs to 'dist', CRA outputs to 'build'
    build_output = "dist" if framework_info["framework"] == "vite" else "build"
    
    return f"""# Production Dockerfile for React

# Stage 1: Build
FROM node:22-alpine as builder

WORKDIR /app

# Set production environment for optimization
ENV NODE_ENV=production

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginxinc/nginx-unprivileged:alpine

# Install curl for healthcheck
USER root
RUN apk add --no-cache curl
USER nginx

COPY --from=builder /app/{build_output} /usr/share/nginx/html

# Expose port 8080 (unprivileged default)
EXPOSE 8080

# Overwrite default nginx config for SPA routing (Optional but recommended)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \\
    CMD curl --silent --output /dev/null http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""


def _generate_dev_dockerfile(framework_info: dict) -> str:
    dev_cmd = framework_info["dev_cmd"]
    dev_port = framework_info["dev_port"]
    framework = framework_info["framework"]
    
    # Framework-specific host binding
    if framework == "vite":
        # Vite needs --host flag to bind to 0.0.0.0
        cmd_line = f'CMD ["npx", "vite", "--host", "0.0.0.0", "--port", "{dev_port}"]'
    elif framework == "next":
        cmd_line = f'CMD ["npx", "next", "dev", "-H", "0.0.0.0", "-p", "{dev_port}"]'
    else:
        # CRA and others respect HOST env var
        cmd_line = f'CMD ["npm", "run", "{dev_cmd}"]'
    
    return f"""# Development Dockerfile for {framework.upper() if framework != "unknown" else "React"}
FROM node:22-alpine

WORKDIR /app

# Bind to all interfaces so Docker port mapping works
ENV HOST=0.0.0.0

COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE {dev_port}

{cmd_line}
"""
