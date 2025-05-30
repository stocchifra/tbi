# Multi-stage build for single-container deployment
FROM node:18-alpine as frontend-build

# Build frontend
WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm ci --only=production
COPY src/frontend ./
# Set API URL to empty string so frontend uses same origin (nginx proxy)
ENV REACT_APP_API_URL=""
RUN npm run build

# Python backend stage
FROM python:3.11-slim as backend-build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage - nginx + python
FROM python:3.11-slim

# Install nginx, supervisor, and curl for health checks
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-build /usr/local/bin /usr/local/bin

# Copy backend application
WORKDIR /app
COPY src/app ./src/app
COPY requirements.txt .

# Copy tests to the expected location for test execution
RUN mkdir -p /home/src
COPY src/tests /home/src/tests
COPY src/app /home/src/app

# Copy frontend build
COPY --from=frontend-build /app/frontend/build /var/www/html

# Copy nginx configuration
RUN rm /etc/nginx/sites-enabled/default
COPY nginx-single.conf /etc/nginx/sites-available/default
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directory
RUN mkdir -p /app/data

# Install test dependencies (including psutil for memory tests)
RUN pip install --no-cache-dir pytest pytest-asyncio httpx psutil

# Set environment variables
ENV DATABASE_URL=sqlite:///data/app.db
ENV SECRET_KEY=development_secret_key_change_in_production
ENV ENVIRONMENT=production
ENV SIMULATE_OPENAI_KEY=0
ENV PYTHONPATH=/home/src:/home

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start supervisor to manage both nginx and backend
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 