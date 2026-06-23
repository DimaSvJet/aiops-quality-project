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

9. Verification Guide

## 9.1. Verify FastAPI service

    Start service:

        ```bash
        uvicorn app.main:app --reload
        ```

    Open:

        ```
        http://127.0.0.1:8000/docs
        ```

    Health endpoint:

        ```
        http://127.0.0.1:8000/health
        ```

    Expected response:

        ```json
        {
        "status": "healthy",
        "model_loaded": true,
        "model_path": "model/model.pkl",
        "webhook_configured": false
        }
        ```

## 9.2. Verify Prometheus metrics

    Open:

        ```
        http://127.0.0.1:8000/metrics
        ```

    Available metrics:

        - prediction_requests_total
        - drift_detected_total
        - prediction_latency_seconds

    Prometheus target page:

        ```
        http://localhost:9090/targets
        ```

    Target status should be UP.

## 9.3. Verify Grafana dashboard

    Open:

        ```
        http://localhost:3000
        ```

    Dashboard contains:

        - Prediction requests
        - Prediction latency
        - Drift events

    Prometheus datasource is used for visualization.

## 9.4. Verify logging with Loki and Promtail

    Generate requests:

        ```json
        {
        "value": 50
        }
        ```

    and

        ```json
        {
        "value": 250
        }
        ```

    Logs are written into:

        ```
        app.log
        ```

    Promtail sends logs to Loki.

    In Grafana:

        ```
        Explore → Loki
        ```

    Query:

        ```logql
        {job="aiops-quality-service"}
        ```

    Example log entries:

        ```
        INFO Input=50.0, prediction=100.0, drift=False
        WARNING Drift detected: input=250.0, prediction=500.0
        ```

## 9.5. Verify drift detector

    Drift rule:

        ```python
        abs(valu1e) > 100
        ```

    Example request:

        ```json
        {
        "value": 250
        }
        ```

    Response:

        ```json
        {
        "input1": 250,
        "predi1ction": 500,
        "drift1_detected": true
        }
        ```

    Drift event:

        - increments drift_detected_total metric;
        - writes1 warning into app.log;
        - optionally triggers retraining webhook.

## 9.6. Verify GitHub Actions retraining pipeline

    Open:

        ```
        GitHub → Actions → Retrain model pipeline
        ```

    Pipeline stages:
        1. Checkout repository
        2. Setup Python
        3. Install dependencies
        4. Run train.py
        5. Build Docker image
        6. Show created artifacts

    Workflow can be triggered manually.

## 9.7. Update model

    Retrain model:

        ```bash
        python model/train.py
        ```

    Generated files:

        ```
        model/model.pkl
        model/version.txt
        ```

    Restart FastAPI:

        ```bash
        uvicorn app.main:app --reload
        ```

    Verify:

        ```
        http://127.0.0.1:8000/health
        ```

    Model should be loaded successfully:

        ```json
        {
        "model_loaded": true
        }
        ```

## 9.8. Verify Helm chart

    Lint chart:

        ```bash
        helm lint helm
        ```

    Render manifests:

        ```bash
        helm template aiops-quality-service helm
        ```

    Deployment contains:
        - image
        - port
        - MODEL_PATH
        - RETRAIN_WEBHOOK_URL

## 9.9. Verify ArgoCD

    Application:

        ```
        argocd/application/application.yaml
        ```

    Auto-sync settings:
        ```yaml
        prune: true
        selfHeal: true
        ```

    ArgoCD automatically synchronizes Kubernetes manifests.

10. Architecture

    FastAPI
    ↓
    Prometheus metrics
    ↓
    Prometheus
    ↓
    Grafana

    FastAPI
    ↓
    app.log
    ↓
    Promtail
    ↓
    Loki
    ↓
    Grafana Explore

    Drift detector
    ↓
    Webhook
    ↓
    GitHub Actions
    ↓
    Retraining
    ↓
    New model