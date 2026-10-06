import os
import time
import joblib
import pandas as pd
from preprocessing import preprocess

_model = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.joblib"))

def predict_reading(record):
    """record (dict) -> (prediction, confidence). 0 = genuine, 1 = fake."""
    X = preprocess(record)
    proba = _model.predict_proba(X)[0]
    prediction = int(proba.argmax())
    confidence = float(proba[prediction])
    return prediction, confidence

if __name__ == "__main__":
    records = pd.read_csv("sensor_data.csv").head(500).to_dict("records")
    correct, start = 0, time.perf_counter()
    for i, rec in enumerate(records):
        pred, conf = predict_reading(rec)
        correct += (pred == rec["label"])
        if i < 3:
            print("Example:", rec["node_id"], "->", pred, round(conf, 3),
                  "(true label:", rec["label"], ")")
    ms = (time.perf_counter() - start) / len(records) * 1000
    print("Accuracy on 500 rows:", correct / len(records))
    print("Average time per reading: %.2f ms" % ms)