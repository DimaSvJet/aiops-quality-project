from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import logging

app = FastAPI(title="AIOps Quality Inference Service")

logging.basicConfig(level=logging.INFO)

REQUEST_COUNT = Counter(
    "prediction_requests_total",
    "Total number of prediction requests"
)

DRIFT_COUNT = Counter(
    "drift_detected_total",
    "Total number of detected drift events"
)

LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction latency in seconds"
)


class InputData(BaseModel):
    value: float


def predict(value: float) -> float:
    return value * 2


def detect_drift(value: float) -> bool:
    return abs(value) > 100


@app.get("/")
def root():
    return {"status": "ok", "service": "aiops-quality-project"}


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
    else:
        logging.info(
            f"Input={data.value}, prediction={prediction}, drift={drift}")

    LATENCY.observe(time.time() - start_time)

    return {
        "input": data.value,
        "prediction": prediction,
        "drift_detected": drift
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
