# syntax=docker/dockerfile:1

### STAGE 1: Build frontend ###
FROM node:slim AS frontend-builder
WORKDIR /app
# Install dependencies for building the frontend.
COPY frontend/package*.json ./frontend/
COPY frontend/tsconfig.json ./frontend/
RUN cd frontend && npm install

# Should the destination be /app/frontend/src?
COPY frontend/src ./frontend/src
COPY frontend/public ./frontend/public
RUN cd frontend && npm run build

### STAGE 2: Build backend ###
FROM python:3.12-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Required, since FROM stage starts with a fresh state
WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies for the backend, NOTE: we're already in the /app directory.
COPY backend/app ./backend/app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy built frontend from previous stage
# We store it temporarily so NGINX can access it via volume
# Copy everything from the build folder, to the /app/frontend_build mount point, 
# since parcel uses subfolders (for workers and assets).
COPY --from=frontend-builder /app/frontend/build/ /app/frontend_build

EXPOSE 8000

# Could this be ./backend/app? NO, workdir paths should be absolute paths.
WORKDIR /app/backend/app
# Run the application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]