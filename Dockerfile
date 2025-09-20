# Multi-stage build for production deployment
FROM node:18-alpine AS frontend-builder

# Accept build arguments from EasyPanel
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_WEBHOOK_URL

# Set working directory for frontend build
WORKDIR /app

# Copy frontend package files first for better Docker layer caching
COPY frontend/package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Set environment variables for Vite build BEFORE copying files
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_WEBHOOK_URL=$VITE_WEBHOOK_URL

# Create .env file for Vite build (with all required variables)
RUN echo "VITE_SUPABASE_URL=$VITE_SUPABASE_URL" > .env && \
    echo "VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY" >> .env && \
    echo "VITE_WEBHOOK_URL=$VITE_WEBHOOK_URL" >> .env

# Copy frontend source code explicitly (only files that exist)
COPY frontend/src/ ./src/
COPY frontend/index.html ./
COPY frontend/vite.config.ts ./
COPY frontend/tsconfig.json ./
COPY frontend/tsconfig.app.json ./
COPY frontend/tsconfig.node.json ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./

# Build frontend for production
RUN npm run build

# Main application stage
FROM python:3.11-slim AS production

# Accept build arguments for all environment variables
ARG WORKANA_EMAIL
ARG WORKANA_PASSWORD
ARG PORT=8000
ARG HOST=0.0.0.0
ARG DEBUG=false
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_WEBHOOK_URL

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV WORKANA_EMAIL=$WORKANA_EMAIL
ENV WORKANA_PASSWORD=$WORKANA_PASSWORD
ENV PORT=$PORT
ENV HOST=$HOST
ENV DEBUG=$DEBUG
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
ENV VITE_WEBHOOK_URL=$VITE_WEBHOOK_URL

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create .env file for backend with all environment variables
RUN echo "WORKANA_EMAIL=$WORKANA_EMAIL" > .env && \
    echo "WORKANA_PASSWORD=$WORKANA_PASSWORD" >> .env && \
    echo "PORT=$PORT" >> .env && \
    echo "HOST=$HOST" >> .env && \
    echo "DEBUG=$DEBUG" >> .env && \
    echo "VITE_SUPABASE_URL=$VITE_SUPABASE_URL" >> .env && \
    echo "VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY" >> .env && \
    echo "VITE_WEBHOOK_URL=$VITE_WEBHOOK_URL" >> .env

# Copy application code
COPY src/ ./src/
COPY main.py .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/dist ./frontend/dist

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && mkdir -p /home/appuser && chown appuser:appuser /home/appuser
RUN chown -R appuser:appuser /app
USER appuser

# Install Playwright browsers as appuser
RUN playwright install chromium

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Command to run the application
CMD ["python", "main.py"]