# Docker Production Guide

This guide details how to build, run, and scale the AI Resume Intelligence Platform in a containerized production environment using Docker and Nginx.

## Production Topology

The production compose stack runs:
*   **Nginx Reverse Proxy**: Entry point, load balancer, body size limiting, SSL termination, and WebSocket forwarder.
*   **FastAPI API instances**: Multiple app processes (e.g. `api_1`, `api_2`) behind Nginx.
*   **Celery Workers**: Scaled workers listening to task events in Redis.
*   **Prometheus / Loki / Grafana**: Monitoring and log aggregation stack.

---

## 1. Create docker-compose.prod.yml

We use `docker-compose.prod.yml` to run the stateful backend containers.

To deploy Nginx as a reverse proxy alongside the backend, add an `nginx` service to `docker-compose.prod.yml` or run Nginx on the host.

### Nginx Service Definition

```yaml
  nginx:
    image: nginx:alpine
    container_name: resume-prod-nginx
    ports:
      - "80:80"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    networks:
      - resume_net
```

---

## 2. Build Production Images

Build optimized production Docker images for the API and worker:

```bash
docker compose -f docker-compose.prod.yml build
```

---

## 3. Running and Scaling Services

Run the stack in detached mode:

```bash
docker compose -f docker-compose.prod.yml up -d
```

### Scaling the stateless API and workers

Scale API backend instances to 3 nodes and worker tasks to 4 nodes to handle high load:

```bash
docker compose -f docker-compose.prod.yml up -d --scale api=3 --scale worker=4
```

Nginx automatically routes traffic statelessly to the scaled `api` container instances.

---

## 4. Run database migrations

Ensure database tables and composite indexes are applied:

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

---

## 5. Validate Health Status

Verify health probe from the proxy container:

```bash
curl -i http://localhost/api/ready
```
Verify that it returns `200 OK`.
