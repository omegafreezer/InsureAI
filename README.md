# InsureAI — Intelligent P&C Claims Risk & Fraud Detection Platform

InsureAI is an end-to-end, enterprise-style insurance claims intelligence platform designed around a Property & Casualty (P&C) insurance workflow.

The system accepts insurance claims through REST APIs, validates claim data, combines supervised fraud classification with unsupervised anomaly detection, produces a risk score, routes claims through automated decision workflows, and provides a human investigation path for higher-risk cases.

It is built as a portfolio project to demonstrate software engineering, AI/ML, REST APIs, data modeling, authentication, testing, Agile/SDLC practices, Docker, and enterprise workflow design.

---

## Why InsureAI?

Insurance claims teams need to process large volumes of claims while identifying suspicious behavior efficiently. InsureAI demonstrates a practical human-in-the-loop approach:

```text
Claim Submission
       ↓
Data Validation
       ↓
ML Risk Scoring
       ↓
Fraud Probability + Anomaly Score
       ↓
Combined Risk Score
       ↓
┌───────────────────┬────────────────────┐
│ Low Risk          │ High Risk          │
│ Auto Approval     │ Manual Investigation│
└───────────────────┴────────────────────┘
                         ↓
                 Investigator Decision
                    Approve / Reject
```

The project intentionally combines automation with human review rather than treating an ML prediction as the final business decision.

---

## Key Features

### 1. Claim Intake & Validation

- Create claims through a REST API and web interface.
- Validate required fields and numeric ranges using Pydantic.
- Store policies, claims, users, and audit records in a relational database.
- Generate unique claim numbers automatically.

### 2. AI/ML Risk Assessment

InsureAI uses two complementary ML approaches:

- Supervised classification using Random Forest and XGBoost.
- Unsupervised anomaly detection using Isolation Forest.
- The training pipeline compares classifier performance using ROC-AUC and persists the selected model.
- Claim features are converted into fraud probability, anomaly score, and an application-level risk score.

### 3. Automated Decision Engine

Configurable thresholds route claims based on their risk score:

```text
Risk score < 35      → AUTO_APPROVED
35 ≤ score < 65      → SUBMITTED / REVIEW
Risk score ≥ 65      → INVESTIGATION
```

These thresholds are configurable through environment variables.

### 4. Human Investigation Workflow

High-risk claims can be reviewed by authorized investigators or administrators.

Supported outcomes include:

- Approve
- Reject
- Mark as Paid

Each decision can include an investigation note and is recorded in the audit log.

### 5. Role-Based Access Control

Three application roles are included:

| Role | Responsibilities |
|---|---|
| ADMIN | Full dashboard access, claim decisions, audit access |
| AGENT | Create and view claims |
| INVESTIGATOR | Review claims and submit investigation decisions |

Authentication uses JWT bearer tokens and password hashing with bcrypt through Passlib.

### 6. Dashboard Analytics

The dashboard exposes operational metrics including:

- Total claims
- High-risk claims
- Investigations
- Approved claims
- Average risk score
- Total claim amount
- Risk-level distribution

### 7. Audit Logging

Important system actions are stored in an audit trail, including claim creation, re-scoring, and investigator decisions.

### 8. API Testing & Documentation

The backend is built with FastAPI and automatically provides interactive OpenAPI/Swagger documentation at `/docs`.

Postman can be used to test the REST endpoints and authentication flow.

---

## Technology Stack

### Frontend

- React.js
- React Router
- Axios
- Recharts
- Vite
- Nginx

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- JWT authentication
- Passlib / bcrypt

### Machine Learning

- Scikit-learn
- XGBoost
- Pandas
- NumPy
- Joblib

### Database

- PostgreSQL 16
- SQLAlchemy ORM

### DevOps / Engineering

- Docker
- Docker Compose
- Git / GitHub
- Pytest
- Postman
- CI/CD-ready structure

---

## System Architecture

```text
                         ┌───────────────────────┐
                         │      React Frontend   │
                         │ Dashboard / Claims    │
                         │ Login / Investigation │
                         └───────────┬───────────┘
                                     │
                                HTTP / JSON
                                     │
                         ┌───────────▼───────────┐
                         │      FastAPI API      │
                         │ Auth / Claims /       │
                         │ Dashboard / Audit     │
                         └───────┬───────┬───────┘
                                 │       │
                      SQLAlchemy │       │ ML inference
                                 │       │
                    ┌────────────▼─┐   ┌─▼─────────────────┐
                    │ PostgreSQL   │   │ ML Service        │
                    │              │   │ Random Forest     │
                    │ Users        │   │ XGBoost            │
                    │ Policies     │   │ Isolation Forest   │
                    │ Claims       │   │ Risk Scoring       │
                    │ Audit Logs   │   └────────────────────┘
                    └──────────────┘

                         Docker Compose
```

---

## Machine Learning Pipeline

The training pipeline creates a reproducible synthetic P&C claims dataset so the application can run without requiring an external proprietary dataset.

### Input features

The current model uses:

- `claim_amount`
- `previous_claims`
- `claim_frequency_30d`
- `location_risk`
- `mismatch_score`
- `late_report_days`
- `weekend_claim`

### Training flow

```text
Synthetic Claims Dataset
          ↓
Train / Test Split
          ↓
┌───────────────────────┐
│ Random Forest         │
│ XGBoost               │
└───────────┬───────────┘
            ↓
       ROC-AUC Compare
            ↓
     Select Best Model
            ↓
     Persist Model Bundle
            ↓
   Isolation Forest Fit
            ↓
      Runtime Scoring
```

The persisted model bundle contains the selected classifier, anomaly detector, feature metadata, baseline values, and evaluation information needed by the application.

### Important note about the dataset

The included claims dataset is synthetic and exists for demonstration, development, and testing. Model metrics on synthetic data should not be interpreted as production insurance-fraud performance.

---

## Claim Decision Workflow

### Low-risk example

```text
Claim amount: ₹12,500
Previous claims: 0
Claims in last 30 days: 0
Location risk: 0.15
Mismatch score: 0.10
Late report: 1 day

        ↓

Risk score: Low
Fraud probability: Low
Anomaly score: Low

        ↓

AUTO_APPROVED
```

### High-risk example

```text
Claim amount: ₹150,000
Previous claims: 8
Claims in last 30 days: 5
Location risk: 0.90
Mismatch score: 0.85
Late report: 8 days
Weekend claim: Yes

        ↓

Risk score: High
Fraud probability: High
Anomaly score: High

        ↓

INVESTIGATION
        ↓

Investigator → Approve / Reject
```

---

## REST API Endpoints

### Authentication

```text
POST   /api/auth/login
GET    /api/auth/me
```

### Claims

```text
POST   /api/claims
GET    /api/claims
GET    /api/claims/{claim_id}
POST   /api/claims/{claim_id}/rescore
POST   /api/claims/{claim_id}/decision
```

### Dashboard

```text
GET    /api/dashboard/summary
GET    /api/dashboard/risk-distribution
```

### Audit

```text
GET    /api/audit
```

### Health

```text
GET    /health
GET    /
```

Full interactive API documentation is available through FastAPI Swagger UI at:

```text
http://localhost:8000/docs
```

---

## Database Model

The relational design includes four main entities:

```text
User
 │
 ├──────────────┐
 │              │
 ▼              ▼
Claims        AuditLog
 │
 ▼
Policy
```

### User

Stores application users, roles, password hashes, account status, and profile information.

### Policy

Stores policy number, customer, policy type, location, and policy start date.

### Claim

Stores claim details, behavioral signals, ML outputs, risk level, workflow status, and decision reason.

### AuditLog

Stores user actions and claim-related events for traceability.

---

## Project Structure

```text
InsureAI/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── claims.py
│   │   │   ├── dashboard.py
│   │   │   └── audit.py
│   │   ├── services/
│   │   │   └── ml_service.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── seed.py
│   │   └── main.py
│   ├── data/
│   │   └── synthetic_claims.csv
│   ├── ml/
│   │   └── train_model.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_health.py
│   │   └── test_model.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Quick Start with Docker

Docker Desktop is the recommended way to run the full application locally.

### Prerequisites

- Windows 10/11, macOS, or Linux
- Docker Desktop / Docker Engine with Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/your-username/InsureAI.git
cd InsureAI
```

### 2. Build and start the application

```bash
docker compose up --build
```

The first build downloads the required dependencies and creates the PostgreSQL, backend, and frontend containers.

### 3. Open the application

Frontend:

```text
http://localhost:5173
```

Backend Swagger:

```text
http://localhost:8000/docs
```

Backend health check:

```text
http://localhost:8000/health
```

### 4. Stop the application

```bash
docker compose down
```

To remove the local PostgreSQL volume as well:

```bash
docker compose down -v
```

---

## Demo Accounts

The application seeds demo users on first startup.

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Agent | `agent` | `Agent@123` |
| Investigator | `investigator` | `Invest@123` |

These credentials are for local demonstration only. Replace them and the JWT secret before any non-demo deployment.

---

## Local Development Without Docker

### Backend

From the project root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Train the model bundle:

```bash
python -m ml.train_model
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

For local development, configure the backend database using `backend/.env` based on `backend/.env.example`.

---

## Testing

The backend includes Pytest tests for health, authentication, and model behavior.

```bash
cd backend
pytest -q
```

API behavior can additionally be tested through:

- FastAPI Swagger UI
- Postman
- Browser-based frontend workflows

---

## Agile / SDLC Plan

The project can be developed and presented as a six-sprint Agile implementation:

### Sprint 1 — Foundation

- Repository setup
- Project architecture
- Authentication
- RBAC
- Database schema

### Sprint 2 — Claim Management

- Policy creation
- Claim intake
- Validation
- Persistence
- Audit logging

### Sprint 3 — ML Risk Engine

- Synthetic dataset generation
- Random Forest
- XGBoost
- Isolation Forest
- Model comparison
- Model persistence

### Sprint 4 — Decision Workflow

- Risk scoring
- Auto-approval rules
- Investigation routing
- Investigator decisions

### Sprint 5 — Frontend & Testing

- Dashboard
- Claims interface
- Investigation interface
- API testing
- Unit testing
- Bug fixing

### Sprint 6 — Deployment Readiness

- Dockerization
- Configuration management
- Documentation
- CI/CD integration
- Cloud deployment planning

---

## Engineering Decisions

### Why combine supervised and unsupervised ML?

A classifier can learn patterns represented in the training labels, while anomaly detection can surface unusual behavior that may not match known fraud examples. Using both gives the decision engine two complementary signals.

### Why keep a human investigation step?

An automated fraud score should support investigators rather than replace them. High-risk claims are routed for review so a human can make the final decision and record the reasoning.

### Why use configurable thresholds?

Risk thresholds can vary by business policy. Keeping them in configuration makes the workflow easier to tune without changing application code.

### Why use audit logs?

Insurance workflows require traceability. Recording claim creation, re-scoring, and decision events creates a basic history of important system actions.

---

## Security Notes

This project includes basic application security for a portfolio environment:

- JWT-based authentication
- Password hashing
- Role-based authorization
- Input validation
- Protected API routes
- Audit logging

For production use, additional controls would be required, including secret management, HTTPS, stronger credential policies, centralized logging, security scanning, rate limiting, PII governance, key rotation, and managed database infrastructure.

---

## Production / Cloud Roadmap

The current project is designed to be containerized and cloud-deployable but should be considered a local/demo system until the following hardening work is completed:

- Deploy backend containers to AWS infrastructure.
- Use managed PostgreSQL instead of the local container database.
- Store model artifacts in object storage such as S3.
- Add CI/CD pipelines with automated testing and security checks.
- Add centralized logs and application metrics.
- Move credentials and secrets to a managed secrets service.
- Add TLS/HTTPS and an API gateway or reverse proxy.
- Establish model monitoring and retraining procedures.
- Define retention, privacy, and PII governance controls.

---

## What This Project Demonstrates

InsureAI brings together:

```text
Python / FastAPI
        +
REST APIs / JSON / HTTP
        +
SQL / Relational Data Modeling
        +
Java-style OOP and layered software design concepts
        +
Machine Learning
        +
Fraud Detection / Anomaly Detection
        +
React Web Application
        +
Authentication / RBAC
        +
Testing / Debugging
        +
Agile / SDLC
        +
Docker / Cloud Readiness
        ↓
End-to-End Enterprise Software Workflow
```

---

## Future Enhancements

Potential next iterations include:

- SHAP-based model explanations for individual claims.
- Document/image evidence ingestion for claims.
- External weather and geospatial risk feeds.
- Model monitoring and drift detection.
- Asynchronous processing with a message queue.
- Notification services for investigators.
- CI/CD with automated security scanning.
- AWS deployment with managed PostgreSQL and object storage.

---

## Disclaimer

InsureAI is an educational and portfolio project. It uses synthetic claim data and simplified business rules. It is not intended for real insurance underwriting, claims settlement, fraud investigation, or production decision-making without appropriate validation, governance, compliance review, and domain expertise.

---

## License

This project is intended for educational and portfolio use. Add a project-specific open-source license if you plan to distribute or modify the repository publicly.
