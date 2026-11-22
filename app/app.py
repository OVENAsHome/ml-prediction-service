import json
import os
import pickle
import time
import urllib.request

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

app = Flask(__name__)

# Загрузка модели
MODEL_PATH = os.getenv("MODEL_PATH", "model/model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

MODEL_VERSION = "v1.0"
METRICS_PATH = os.path.join(os.path.dirname(MODEL_PATH), "metrics.json")
LOGGER_URL = os.getenv("LOGGER_URL", "http://logger-service:5001/log")

# Метрики
PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total", "Total predictions", ["model_version", "predicted_class"]
)
PREDICTION_LATENCY = Histogram("ml_prediction_latency_seconds", "Prediction latency")
PREDICTION_CONFIDENCE = Histogram(
    "ml_prediction_confidence", "Probability of the predicted class",
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
)
LOGGER_ERRORS_TOTAL = Counter("ml_logger_errors_total", "Logger service errors")
MODEL_INFO = Gauge("ml_model_info", "Model info", ["version"])
MODEL_INFO.labels(version=MODEL_VERSION).set(1)
MODEL_ACCURACY = Gauge("ml_model_accuracy", "Model accuracy on the test set")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        MODEL_ACCURACY.set(json.load(f).get("accuracy", 0))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "prediction"})


@app.route("/predict", methods=["POST"])
def predict():
    start = time.time()
    data = request.get_json(force=True)
    features = data.get("features", [])
    if not features:
        return jsonify({"error": "No features provided"}), 400
    if len(features) != model.n_features_in_:
        return jsonify({"error": f"Expected {model.n_features_in_} features"}), 400

    pred = model.predict([features])[0]
    proba = max(model.predict_proba([features])[0])
    result = {"class": int(pred), "probability": float(proba)}

    PREDICTION_LATENCY.observe(time.time() - start)
    PREDICTIONS_TOTAL.labels(model_version=MODEL_VERSION, predicted_class=str(pred)).inc()
    PREDICTION_CONFIDENCE.observe(float(proba))

    # Вызов logger-service по REST API
    payload = json.dumps({
        "input_data": {"features": features},
        "prediction": result,
        "model_version": MODEL_VERSION,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            LOGGER_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status >= 400:
                LOGGER_ERRORS_TOTAL.inc()
                app.logger.warning(f"Logger returned {resp.status}")
    except Exception as e:
        LOGGER_ERRORS_TOTAL.inc()
        app.logger.error(f"Logger service error: {e}")

    return jsonify(result)


@app.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
