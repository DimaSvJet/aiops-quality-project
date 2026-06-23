import logging
import os
import pickle
import time
from typing import Optional

import requests
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="AIOps Quality Inference Service")

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

MODEL_PATH = os.getenv("MODEL_PATH", "model/model.pkl")
RETRAIN_WEBHOOK_URL = os.getenv("RETRAIN_WEBHOOK_URL", "")

model: Optional[object] = None

REQUEST_COUNT = Counter(
    "prediction_requests_total",
    "Total number of prediction requests",
)

DRIFT_COUNT = Counter(
    "drift_detected_total",
    "Total number of detected drift events",
)

LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction latency in seconds",
)


class InputData(BaseModel):
    value: float


class FallbackModel:
    def predict(self, value: float) -> float:
        return value * 2


@app.on_event("startup")
def load_model():
    global model

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        logging.info(f"Model loaded from {MODEL_PATH}")
    except Exception as exc:
        model = FallbackModel()
        logging.warning(
            f"Could not load model from {MODEL_PATH}. Fallback model is used. Error: {exc}")


def predict(value: float) -> float:
    if model is None:
        raise RuntimeError("Model is not initialized")

    if isinstance(model, dict):
        coef = float(model.get("coef", 2.0))
        bias = float(model.get("bias", 0.0))
        return coef * value + bias

    return float(model.predict(value))


def detect_drift(value: float) -> bool:
    return abs(value) > 100


def trigger_retrain_webhook(value: float, prediction: float):
    if not RETRAIN_WEBHOOK_URL:
        logging.info(
            "RETRAIN_WEBHOOK_URL is not configured. Webhook call skipped.")
        return

    try:
        response = requests.post(
            RETRAIN_WEBHOOK_URL,
            json={
                "event": "drift_detected",
                "input": value,
                "prediction": prediction,
            },
            timeout=5,
        )
        logging.info(
            f"Retrain webhook called. Status code: {response.status_code}")
    except Exception as exc:
        logging.error(f"Failed to call retrain webhook: {exc}")


@app.get("/")
def root():
    return {"status": "ok", "service": "aiops-quality-project"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "webhook_configured": bool(RETRAIN_WEBHOOK_URL),
    }


@app.post("/predict")
def predict_endpoint(data: InputData):
    start_time = time.time()
    REQUEST_COUNT.inc()

    prediction = predict(data.value)
    drift = detect_drift(data.value)

    if drift:
        DRIFT_COUNT.inc()
        logging.warning(
            f"Drift detected: input={data.value}, prediction={prediction}")
        trigger_retrain_webhook(data.value, prediction)
    else:
        logging.info(
            f"Input={data.value}, prediction={prediction}, drift={drift}")

    LATENCY.observe(time.time() - start_time)

    return {
        "input": data.value,
        "prediction": prediction,
        "drift_detected": drift,
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
