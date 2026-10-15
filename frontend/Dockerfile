# Build from the repo root: docker build -f frontend/Dockerfile .
# (docker-compose.yml at the repo root already sets this context)

# --- Stage 1: build the static assets ---
FROM node:20-slim AS builder
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Vite inlines VITE_* env vars into the JS bundle at BUILD time, not runtime -
# there's no "restart the container to pick up a new env var" for these.
# Default points at localhost:8000 because the browser (not the frontend
# container) is what calls the API - the internal Docker network name
# "backend" is not reachable from the browser, only from other containers.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# --- Stage 2: serve the build with nginx ---
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
