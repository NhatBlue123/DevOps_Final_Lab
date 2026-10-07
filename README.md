# User Management API - DevOps CI/CD with GitHub Actions & AWS

[![CI/CD Pipeline](https://github.com/NhatBlue123/DevOps_Final_Lab/actions/workflows/deploy.yml/badge.svg)](https://github.com/NhatBlue123/DevOps_Final_Lab/actions/workflows/deploy.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED.svg?logo=docker)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20S3%20%7C%20RDS-FF9900.svg?logo=amazon-aws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python)](https://www.python.org/)

---

## 1. Project Overview

**User Management API** is a production-ready cloud backend service designed with DevOps best practices. The project demonstrates an automated CI/CD lifecycle using **GitHub Actions**, containerization with **Docker** and **Docker Compose**, and deployment to **Amazon Web Services (AWS)**.

### Core Capabilities

- **RESTful API**: Fast and robust API built with **FastAPI** and **Pydantic v2**.
- **Database Persistence**: Object-relational mapping (ORM) with **SQLAlchemy**, supporting **PostgreSQL** (AWS RDS or containerized) and SQLite for local development.
- **Cloud Object Storage**: File upload and asset management integrated with **Amazon Simple Storage Service (AWS S3)** via `boto3`.
- **Containerization**: Secure, multi-stage production **Dockerfile** running as a non-privileged user (`appuser`) with built-in healthcheck.
- **Continuous Integration (CI)**: Automated code linting with **Flake8** (PEP8 compliance) and unit testing with **Pytest** and coverage reports on every Pull Request and Push.
- **Continuous Deployment (CD)**: Automated deployment pipeline via **GitHub Actions** that securely SSHes into an **AWS EC2** instance, pulls the latest code, rebuilds the Docker image on the instance, restarts container services, and verifies application health.

---

## 2. Architecture Diagram

The system integrates GitHub Actions automation with AWS Cloud infrastructure:

```mermaid
flowchart TD
    subgraph Developer_Environment["Developer Workflow"]
        Dev["Developer"] -->|git push origin main| GH["GitHub Repository"]
    end

    subgraph GitHub_Actions["GitHub Actions CI/CD Pipeline (.github/workflows/deploy.yml)"]
        GH --> CI["Job 1: CI (Lint & Test)"]
        CI -->|Flake8 PEP8 Check| Lint["Linting Pass"]
        CI -->|Pytest Coverage| Test["Unit Tests Pass"]
        Lint & Test --> CD["Job 2: CD (Deploy to EC2)"]
    end

    subgraph AWS_Cloud["AWS Cloud Infrastructure"]
        subgraph EC2_Instance["Amazon EC2 Instance (Ubuntu 22.04 LTS)"]
            SSH["SSH Session (Port 22)"]
            GitPull["git pull origin main"]
            DockerBuild["docker compose build"]
            DockerRun["docker compose up -d"]

            subgraph Containers["Docker Compose Runtime"]
                AppBackend["FastAPI Container (Port 8000)"]
                AppDB["PostgreSQL Container (Port 5432)"]
            end
        end

        subgraph AWS_Managed["AWS Managed Services"]
            S3Bucket["AWS S3 Bucket (Object Storage)"]
            AWSRDS["AWS RDS PostgreSQL (Optional Cloud DB)"]
            IAM["AWS IAM (Access Keys)"]
        end
    end

    CD -->|SSH via EC2_HOST & EC2_SSH_KEY| SSH
    SSH --> GitPull --> DockerBuild --> DockerRun
    DockerRun --> AppBackend
    AppBackend <-->|SQLAlchemy| AppDB
    AppBackend -.->|Alternative Database URL| AWSRDS
    AppBackend <-->|boto3 API (Upload / Read)| S3Bucket
    IAM -.->|Credentials Auth| AppBackend
    Users["End Users / HTTP Clients"] -->|HTTP Requests :8000| AppBackend
```

---

## 3. Prerequisites

Ensure you have the following accounts and tools installed before getting started:

### Accounts

- **GitHub Account**: To host the repository and execute GitHub Actions workflows.
- **AWS Account**: Free Tier eligible account with access to EC2, S3, and IAM.

### Local Development Tools

- **Git** (>= 2.30)
- **Docker** (>= 24.0) & **Docker Compose** (>= 2.20)
- **Python** (>= 3.11)
- **cURL** or Postman (for API testing)

---

## 4. Local Development Setup

### Option A: Running with Docker Compose (Recommended)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/NhatBlue123/DevOps_Final_Lab.git
   cd DevOps_Final_Lab
   ```

2. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   _(Update `.env` with your desired configuration if needed)._

3. **Start the application services:**

   ```bash
   docker compose up -d --build
   ```

4. **Verify running containers:**

   ```bash
   docker compose ps
   ```

5. **Access the application:**
   - API Root: [http://localhost:8000/](http://localhost:8000/)
   - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Healthcheck: [http://localhost:8000/health](http://localhost:8000/health)

6. **Stop services:**
   ```bash
   docker compose down
   ```

---

### Option B: Running Locally with Python Virtual Environment

1. **Navigate to the backend directory and create virtual environment:**

   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - **Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

3. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the FastAPI development server:**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Run Linting and Unit Tests:**

   ```bash
   # PEP8 code styling
   flake8 --config=.flake8 app/ tests/

   # Run Pytest with test coverage report
   pytest -v --cov=app --cov-report=term tests/
   ```

---

## 5. AWS Resources

The following AWS resources are provisioned for this project:

| AWS Resource           | Name / Type                    | Purpose                           | Configuration Details                                        |
| ---------------------- | ------------------------------ | --------------------------------- | ------------------------------------------------------------ |
| **Amazon EC2**         | `t2.micro` or `t3.micro`       | Host containerized application    | Ubuntu 22.04 LTS, Docker & Docker Compose installed          |
| **Security Group**     | `app-ec2-sg`                   | Network firewall for EC2          | Inbound rules: `22` (SSH), `8000` (FastAPI API), `80` (HTTP) |
| **AWS S3 Bucket**      | e.g. `devops-final-app-bucket` | Object storage for uploaded files | Private bucket with IAM programmatic access                  |
| **AWS IAM User**       | `github-actions-deployer`      | Access delegation                 | Policies: `AmazonS3FullAccess`                               |
| **AWS Key Pair**       | `devops-key.pem`               | Secure SSH authentication         | Used by GitHub Actions runner to connect to EC2              |
| **AWS RDS (Optional)** | `db.t3.micro` PostgreSQL       | Production managed database       | Multi-AZ disabled for Free Tier                              |

---

## 6. Environment Variables

The application and CI/CD pipeline require the following environment variables:

| Variable Name           | Description                              | Required In              | Example / Value                                                     |
| ----------------------- | ---------------------------------------- | ------------------------ | ------------------------------------------------------------------- |
| `DATABASE_URL`          | SQLAlchemy PostgreSQL connection URL     | `.env` / GitHub Secret   | `postgresql+psycopg2://postgres:postgres123@db:5432/userdb`         |
| `AWS_ACCESS_KEY_ID`     | AWS IAM programmatic access key ID       | `.env` / GitHub Secret   | `AKIAIOSFODNN7EXAMPLE`                                              |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM programmatic secret access key   | `.env` / GitHub Secret   | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`                          |
| `AWS_REGION`            | AWS Region where S3 bucket resides       | `.env`                   | `ap-southeast-1` (Singapore) / `us-east-1`                          |
| `S3_BUCKET_NAME`        | Name of the AWS S3 Bucket                | `.env` / GitHub Secret   | `devops-final-app-storage`                                          |
| `EC2_HOST`              | Public IPv4 address or Public DNS of EC2 | GitHub Secret            | `54.254.123.45`                                                     |
| `EC2_SSH_KEY`           | Content of the `.pem` private SSH key    | GitHub Secret            | `-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----` |
| `EC2_USER`              | EC2 SSH username (Default: `ubuntu`)     | GitHub Secret (Optional) | `ubuntu` (or `ec2-user`)                                            |

---

## 7. Deployment Instructions

### Step 7.1: Prepare the AWS EC2 Instance

1. Launch an **Ubuntu 22.04 LTS** EC2 instance on AWS.
2. Ensure the Security Group permits Inbound traffic on ports **22** (SSH) and **8000** (API).
3. Connect to the instance via SSH:
   ```bash
   ssh -i /path/to/devops-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```
4. Install Docker and Docker Compose plugin on the instance:

   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg lsb-release git

   # Install Docker Engine
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg

   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

   # Grant Docker permissions to ubuntu user
   sudo usermod -aG docker $USER
   newgrp docker
   ```

5. Verify Docker setup:
   ```bash
   docker --version
   docker compose version
   ```

---

### Step 7.2: Configure GitHub Secrets

In your GitHub repository, navigate to:
**Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ **New repository secret**

Create each of the following 6 secrets:

| Secret Name             | Secret Value                                                    |
| ----------------------- | --------------------------------------------------------------- |
| `EC2_HOST`              | Public IPv4 Address of your EC2 instance (e.g. `54.254.123.45`) |
| `EC2_SSH_KEY`           | Entire content of your `.pem` SSH Private Key file              |
| `AWS_ACCESS_KEY_ID`     | Your IAM Access Key ID                                          |
| `AWS_SECRET_ACCESS_KEY` | Your IAM Secret Access Key                                      |
| `S3_BUCKET_NAME`        | Your AWS S3 Bucket Name                                         |
| `DATABASE_URL`          | `postgresql+psycopg2://postgres:postgres123@db:5432/userdb`     |
| `EC2_USER` _(Optional)_ | `ubuntu` (default if omitted)                                   |

---

### Step 7.3: Trigger Automated CI/CD Pipeline

1. **Commit and push changes to the `main` branch:**

   ```bash
   git add .
   git commit -m "feat: complete Part 6 CI/CD pipeline with GitHub Actions"
   git push origin main
   ```

2. **GitHub Actions Workflow Execution:**
   - **Job 1 (Lint & Test)**: Clones code on Ubuntu runner, runs `flake8` for syntax and PEP8 compliance, executes 17 `pytest` unit tests with code coverage.
   - **Job 2 (Deploy to EC2)**:
     - SSHes into the EC2 instance using `appleboy/ssh-action`.
     - Clones or pulls the latest code (`git pull origin main`).
     - Writes production `.env` from GitHub Secrets.
     - Rebuilds the Docker image on the instance (`docker compose build backend`).
     - Restarts containers (`docker compose down && docker compose up -d`).
     - Executes automated health check on `http://localhost:8000/health`.

3. **Verify Deployment on EC2:**
   Open your browser or run:
   ```bash
   curl http://<EC2_PUBLIC_IP>:8000/health
   # Response: {"status":"healthy","service":"user-management-api","version":"1.0.0"}
   ```

---

## 8. API Documentation

Interactive Swagger documentation is automatically available at:
`http://<EC2_PUBLIC_IP>:8000/docs` or `http://localhost:8000/docs`

### Summary of Endpoints

| Method   | Endpoint      | Description                                     | Request Body                                         | Response Codes                               |
| -------- | ------------- | ----------------------------------------------- | ---------------------------------------------------- | -------------------------------------------- |
| `GET`    | `/`           | Root service info                               | None                                                 | `200 OK`                                     |
| `GET`    | `/health`     | Application healthcheck                         | None                                                 | `200 OK`                                     |
| `GET`    | `/users/`     | Get list of users (pagination: `skip`, `limit`) | None                                                 | `200 OK`                                     |
| `POST`   | `/users/`     | Create a new user                               | JSON (`name`, `email`, `phone`, `role`)              | `201 Created`, `400 Bad Request`             |
| `GET`    | `/users/{id}` | Get user details by ID                          | None                                                 | `200 OK`, `404 Not Found`                    |
| `PUT`    | `/users/{id}` | Update existing user information                | JSON (`name`, `email`, `phone`, `role`, `is_active`) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/users/{id}` | Delete user by ID                               | None                                                 | `204 No Content`, `404 Not Found`            |
| `GET`    | `/s3/status`  | Check AWS S3 connectivity status                | None                                                 | `200 OK`                                     |
| `POST`   | `/s3/upload`  | Upload a file to AWS S3 Bucket                  | `multipart/form-data` (`file`)                       | `201 Created`, `400`, `503`                  |
| `GET`    | `/s3/files`   | List all files stored in S3 Bucket              | Query: `prefix` (optional)                           | `200 OK`, `400`, `503`                       |

---

### Example cURL Requests

#### 1. Create a User

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nguyen Van A",
    "email": "nguyenvana@example.com",
    "phone": "0901234567",
    "role": "admin"
  }'
```

#### 2. Get Users List

```bash
curl -X GET "http://localhost:8000/users/?skip=0&limit=10"
```

#### 3. Upload File to AWS S3

```bash
curl -X POST "http://localhost:8000/s3/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@avatar.png"
```

#### 4. List Files from S3 Bucket

```bash
curl -X GET "http://localhost:8000/s3/files"
```

---

## 9. Screenshots & Proof of Deployment

Below are screenshots verifying AWS resource setup and verification:

### 9.1 IAM User Creation & Policies

| IAM User Creation                                      | Attached Policies                                 |
| ------------------------------------------------------ | ------------------------------------------------- |
| ![IAM User Creation](sceenshots/IAM_user_creation.jpg) | ![Attach Policies](sceenshots/attachpolicies.jpg) |

### 9.2 AWS Infrastructure & Verification

| AWS RDS PostgreSQL Database    | AWS STS Caller Identity Verification                                         |
| ------------------------------ | ---------------------------------------------------------------------------- |
| ![AWS RDS](sceenshots/rds.jpg) | ![AWS STS Verification](sceenshots/vertication_aws_sts_get_caller_inden.jpg) |

---

## 10. Submission Deliverables Checklist

- [x] **Source Code**: FastAPI application with modular architecture (`api`, `models`, `schemas`, `config`, `database`).
- [x] **Dockerfile**: Multi-stage build with security hardening (non-root `appuser`) and container `HEALTHCHECK`.
- [x] **docker-compose.yml**: Multi-container setup for `db` (PostgreSQL) and `backend` with all required environment variables.
- [x] **GitHub Actions Workflow**: `.github/workflows/deploy.yml` with lint, test, SSH EC2 deployment, image rebuild, container restart, and healthcheck.
- [x] **README.md**: Complete 8-part documentation with architecture diagram, prerequisites, setup, AWS resources, environment variables, deployment steps, and API docs.
- [x] **Screenshots**: AWS IAM, Policies, RDS, and AWS CLI verification captured in `sceenshots/`.

#### ENDD
