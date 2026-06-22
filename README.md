# AIOps Quality Project

## Overview

This project implements an MLOps pipeline for serving ML predictions, detecting drift, retraining models, and deploying updates using GitOps.

The stack includes:

- FastAPI
- Docker
- Helm
- ArgoCD
- Prometheus
- Grafana
- GitHub Actions

---

## Project structure

```text
aiops-quality-project/
├── app/
├── model/
├── helm/
├── argocd/
├── prometheus/
├── grafana/
├── .github/workflows/
├── Dockerfile
├── requirements.txt
└── README.md

1. Inference service

FastAPI exposes:
    /
    /predict
    /metrics

Example request:
    curl -X POST http://127.0.0.1:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"value":10}'

Response:
    {
    "input": 10,
    "prediction": 20,
    "drift_detected": false
    }

2. Drift detection

Simple drift detector:
    abs(value) > 100

If drift is detected:   
    drift_detected = True

Event is logged and Prometheus counter is increased.

3. Prometheus metrics

Available at: http://127.0.0.1:8000/metrics

Metrics:
    prediction_requests_total   
    drift_detected_total
    prediction_latency_seconds

4. Retraining
Retraining script: model/train.py

Creates:
    model.pkl
    version.txt

Run manually:
    python model/train.py

4. Docker
Build image:
    docker build -t aiops-quality-service .

Run container:
    docker run -p 8000:8000 aiops-quality-service

5. Helm deployment
Validate chart: helm lint helm

Render manifests:
    helm template aiops-quality-service helm

6. ArgoCD
Application manifest:
    argocd/application/application.yaml

Namespace: application

Auto-sync enabled.

7. GitHub Actions

Workflow: .github/workflows/retrain-model.yml

Pipeline stages:
    Checkout repository
    Setup Python
    Install dependencies
    Run retraining
    Build Docker image
    Show model artifacts

Workflow can be triggered manually from GitHub Actions.

8. Grafana Dashboard
Dashboard contains:
    Prediction requests
    Drift detected events
    Prediction latency

9. Verification
9.1. FastAPI
Open: http://127.0.0.1:8000/docs

9.2. Metrics
Open: http://127.0.0.1:8000/metrics

9.3. GitHub Actions

Go to:
Actions → Retrain model pipeline

Check successful workflow execution.

9.4. Helm
Run:
helm lint helm

9.5. Docker

Run:
docker build -t aiops-quality-service .

10. Technologies
    Python 3.12
    FastAPI
    Docker
    Helm
    ArgoCD
    Prometheus
    Grafana
    GitHub Actions