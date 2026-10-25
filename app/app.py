import json
import os
import pickle

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# Загрузка модели при старте
MODEL_PATH = os.getenv("MODEL_PATH", "model/model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

MODEL_VERSION = "v1.0"


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "10.10.10.101"),
        dbname=os.getenv("DB_NAME", "ml_predictions"),
        user=os.getenv("DB_USER", "ml_app"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    features = data.get("features", [])
    if not features:
        return jsonify({"error": "No features provided"}), 400
    if len(features) != model.n_features_in_:
        return jsonify({"error": f"Expected {model.n_features_in_} features"}), 400

    pred = model.predict([features])[0]
    proba = max(model.predict_proba([features])[0])
    result = {"class": int(pred), "probability": float(proba)}

    # Запись в БД
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO predictions (input_data, prediction, model_version) VALUES (%s, %s, %s)",
        (json.dumps({"features": features}), json.dumps(result), MODEL_VERSION),
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
