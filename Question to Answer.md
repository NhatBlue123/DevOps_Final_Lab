### 1. Explain why multi-stage builds are used in the Dockerfile and how they improve both image size and security.

- **Image Size Reduction**: 
  - The build stage installs all required packages inside a clean virtual environment (`/opt/venv`).
  - The final runner stage only copies `/opt/venv` and the application source code, leaving behind cached files, build tools, and package managers. This keeps the final image lightweight.

- **Security Improvements**:
  - Separates the build environment from the runtime environment. Attackers cannot leverage compiler tools or build utilities if the container is compromised.
  - Runs the container as a dedicated non-root user (`appuser`), preventing unauthorized privilege escalation inside the container.

- **Build Performance & Caching**:
  - Dependency installation and code copying are separated into distinct layers. Rebuilding after code edits skips dependency re-installation, speeding up CI/CD pipeline execution.

---

### 2. Describe the complete CI/CD pipeline flow from a developer pushing code to the application being deployed in production.

1. **Code Push**: Developer pushes code or opens a Merge Request on GitLab.
2. **Lint Stage (`backend:lint`)**: Runs `flake8` and `py_compile` to verify Python syntax and PEP8 style compliance.
3. **Test Stage (`backend:test`)**: Executes Pytest unit tests against an isolated database fixture, producing `coverage.xml` and `junit.xml` test reports.
4. **Scan Stage (`sonarqube:scan`)**: SonarQube Scanner ingests `coverage.xml`, performs static code analysis, and evaluates Quality Gate status.
5. **Build Stage (`docker:build`)**: If the scan passes, Docker-in-Docker builds the multi-stage image and pushes tagged images to GitLab Container Registry (`$CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA`).
6. **Deploy Stage (`deploy:bluegreen`)**: Executes zero-downtime Blue-Green deployment:
   - Starts target container (`backend_blue` or `backend_green`).
   - Performs health check polling on `/health`.
   - On success: reloads Nginx router to switch traffic and stops the old container.
   - On failure: triggers automatic rollback, keeping the current live slot running.

---

### 3. How does the SonarQube quality gate integrate with the pipeline, and what happens when the gate fail?

- **Integration**:
  - The `sonarqube:scan` job runs SonarQube Scanner CLI configured via `sonar-project.properties`.
  - It sends source code and test coverage reports (`coverage.xml`) to the SonarQube server for evaluation.
  - The flag `-Dsonar.qualitygate.wait=true` forces the scanner to wait synchronously for the server's Quality Gate result.

- **Failure Behavior**:
  - If code coverage falls below threshold, or if security vulnerabilities/bugs are detected, SonarQube marks the Quality Gate as **FAILED**.
  - The scanner process exits with error code 1.
  - Because `allow_failure: false` is set on the job, GitLab CI immediately fails the stage.
  - The downstream `build` and `deploy` stages are **strictly blocked**, preventing unverified or failing code from being built or deployed to production.

---

### 4. Describe the GitHub Actions CI/CD Pipeline flow (Part 6)

1. **Trigger**: Developer pushes code to the `main` branch or opens a Pull Request (`.github/workflows/deploy.yml`).
2. **CI Stage (`test` Job)**:
   - Sets up Python 3.11 runner with dependency caching.
   - Installs packages from `backend/requirements.txt`.
   - Executes `flake8` to enforce PEP8 syntax and coding standards.
   - Executes `pytest` with code coverage reports across all unit tests.
3. **CD Stage (`deploy` Job)**:
   - Runs strictly after `test` passes and only on pushes to `main`.
   - SSHes securely into AWS EC2 using `EC2_HOST` and `EC2_SSH_KEY` via `appleboy/ssh-action`.
   - Clones or pulls the latest code from GitHub repository (`git pull origin main`).
   - Writes production `.env` securely using GitHub Secrets (`DATABASE_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`).
   - Rebuilds the multi-stage Docker image directly on the EC2 instance (`docker compose build backend`).
   - Restarts the containers (`docker compose down && docker compose up -d`).
   - Performs automated healthcheck verification on `http://localhost:8000/health`.

