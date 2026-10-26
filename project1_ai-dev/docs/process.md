# Development Process

The agent team follows a strict, trackable process:

1. **Planning**: The System Architect Agent defines the scope in `plan.md` and creates tasks in `docs/tasks.md`.
2. **Implementation**: 
   - Backend Agent and Frontend Agent work in parallel on the API and UI.
   - Code is written to follow the defined acceptance criteria.
3. **Testing**: Unit and integration tests are written and executed locally via `make test`.
4. **Observability**: The DevOps agent instruments the code with Prometheus metrics and structured JSON logging.
5. **Review & Tracker Update**: Once tests pass, agents update the status in `docs/tasks.md` to `Done`.
6. **Deployment**: CI/CD pipeline triggers on commit, runs tests, and deploys to the `dev` environment. Production deployments require manual approval.