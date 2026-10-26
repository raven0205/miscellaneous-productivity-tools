# Deployment Demo

Since the AI Marketing System is a backend-driven API with an embedded SQLite database and a vanilla JS frontend, the application is designed to be fully self-contained. 

## Running the Application Locally
You can start the full stack, including Prometheus metrics and Alertmanager, using a single command:

```bash
docker-compose up --build
```

Alternatively, you can use the provided Makefile for the native Python environment:
```bash
make install
make run
```

## Public URL & Deployment
For a production deployment, the application is packaged as a Docker container. The GitHub Actions CI/CD pipeline (`.github/workflows/deploy.yml`) is configured to:
1. **Continuous Integration**: Build the image and run tests automatically on push.
2. **Continuous Deployment (Dev)**: Push the image to a container registry and update the `dev` Kubernetes cluster/environment automatically.
3. **Manual Production Deploy**: Through GitHub Actions' `workflow_dispatch` feature, an administrator can manually trigger the deployment to the production cluster.

### Live Demo Instructions
If deployed to a public server (e.g., AWS EC2, DigitalOcean, or Heroku):
1. Navigate to `http://<YOUR_SERVER_IP>:3000` to view the **Dashboard UI**.
2. Navigate to `http://<YOUR_SERVER_IP>:3000/api/prom-metrics` to view the structured business metrics scraped by Prometheus.
3. Check the application logs via `docker logs <container_id>` to view the structured JSON logs with injected `trace_id`s, ensuring zero customer data leakage.