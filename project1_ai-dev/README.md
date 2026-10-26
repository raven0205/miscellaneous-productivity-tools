# AI-Driven Autonomous Marketing Automation System

A lightweight, self-contained MVP for an AI-driven marketing automation platform. Built with a native Python stack to comply with strict internal regulations, this system demonstrates autonomous campaign generation, human-in-the-loop approvals, and self-healing infrastructure.

## Project Structure

This project follows a modular, agent-driven architecture:
- **`app.py`**: The core Flask backend, SQLite database logic, and API endpoints.
- **`templates/index.html`**: The vanilla JavaScript + Tailwind CSS frontend dashboard.
- **`prometheus/`**: Alerting and observability configurations.
- **`tests/`**: Unit and integration tests for the API and Responder Agent.
- **`docs/`**: Modular documentation defining team structure, processes, and the task tracker.

## Key Features

1. **Agentic Workflows**: Generates AI campaigns (e.g., Abandoned Cart) using a rule engine and LLM concepts.
2. **Human-in-the-Loop**: A dedicated UI queue for marketers to approve or reject AI-generated content.
3. **Structured Telemetry**: JSON-formatted logs with injected Trace IDs (`X-Trace-Id`) for safe, compliant observability without exposing customer data.
4. **Responder Agent**: Uses Prometheus and Alertmanager to catch high campaign rejection rates and automatically pauses AI generation via webhooks.

## Prerequisites

- **Python 3.9+** (Available natively on macOS/Linux)
- **Docker & Docker Compose** (Optional, for running the full observability stack)

## Getting Started

### Option 1: Native Execution (No Docker required)
If you want to run the app using your native Python environment:

1. Install the required Python packages:
   ```bash
   make install
   ```
2. Start the Flask application:
   ```bash
   make run
   ```
3. Open your browser and navigate to: `http://localhost:3000`

### Option 2: Docker Compose (Full Stack)
To run the application alongside Prometheus and Alertmanager for the full Responder Agent experience:

1. Build and start the containers:
   ```bash
   make docker-up
   ```
2. Access the services:
   - **App Dashboard**: `http://localhost:3000`
   - **Prometheus UI**: `http://localhost:9090`
3. Stop the containers:
   ```bash
   make docker-down
   ```

## Running Tests

Execute the unit and integration tests (which include testing the Responder Agent webhook) using:

```bash
make test
```

## Documentation & Architecture

For more details on how the autonomous agents collaborate and the project's architectural decisions, see the [AGENTS.md](AGENTS.md) file, which serves as the entry point to our modular documentation.