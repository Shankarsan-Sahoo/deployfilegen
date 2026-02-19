def generate_frontend_dockerfile(mode: str) -> str:
    """
    Generates a production-ready or dev Dockerfile for React.
    """
    if mode == "dev":
        return _generate_dev_dockerfile()
    else:
        return _generate_prod_dockerfile()

def _generate_prod_dockerfile() -> str:
    return """# Production Dockerfile for React

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Set production environment for optimization
ENV NODE_ENV=production

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginxinc/nginx-unprivileged:alpine

COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 8080 (unprivileged default)
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \\
    CMD curl --silent --output /dev/null http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""

def _generate_dev_dockerfile() -> str:
    return """# Development Dockerfile for React
FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

CMD ["npm", "start"]
"""
