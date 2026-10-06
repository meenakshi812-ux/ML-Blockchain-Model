import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
HERE = os.path.dirname(os.path.abspath(__file__))
SENSORS = ["temperature", "humidity", "pressure"]
RANGES = {
    "temperature": (15, 40),
    "humidity": (30, 90),
    "pressure": (980, 1040),
}

def load_data(path=os.path.join(HERE, "sensor_data.csv")):
    df = pd.read_csv(path)
    df = df.sort_values(["node_id", "timestamp"]).reset_index(drop=True)
    return df

def clean(df):
    # 1. fill missing values with the node's previous value
    df[SENSORS] = df.groupby("node_id")[SENSORS].ffill()
    df[SENSORS] = df[SENSORS].fillna(df[SENSORS].mean())
    # 2. clip out-of-range values
    for s, (lo, hi) in RANGES.items():
        df[s] = df[s].clip(lo, hi)
    return df

WINDOW = 5

def add_features(df):
    for s in SENSORS:
        g = df.groupby("node_id")[s]
        df[s + "_diff"] = g.diff().fillna(0)
        df[s + "_roll_mean"] = g.transform(
            lambda x: x.rolling(WINDOW, min_periods=1).mean())
        df[s + "_roll_std"] = g.transform(
            lambda x: x.rolling(WINDOW, min_periods=1).std()).fillna(0)
        # value minus the average of the OTHER nodes at the same time
        total = df.groupby("timestamp")[s].transform("sum")
        count = df.groupby("timestamp")[s].transform("count")
        others = (total - df[s]) / (count - 1)
        df[s + "_nbr_diff"] = df[s] - others
    return df
FEATURES = SENSORS + [
    s + suffix
    for s in SENSORS
    for suffix in ("_diff", "_roll_mean", "_roll_std", "_nbr_diff")
]

def prepare_training_data(path=os.path.join(HERE, "sensor_data.csv")):
    df = add_features(clean(load_data(path)))
    X, y = df[FEATURES], df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)   # 80/20 like the paper
    scaler = StandardScaler().fit(X_train)                   # fit on TRAIN only
    joblib.dump(scaler, os.path.join(HERE, "scaler.joblib"))  # save for live mode                  # save for live mode
    return scaler.transform(X_train), scaler.transform(X_test), y_train, y_test
# ---------------- LIVE MODE ----------------
from collections import deque
import numpy as np

_scaler = None
_history = {}   # node_id -> last 5 values of each sensor
_latest = {}    # node_id -> latest value of each sensor

def build_features(record):
    """Raw (unscaled) feature row for ONE live reading."""
    node = record["node_id"]
    hist = _history.setdefault(node, {s: deque(maxlen=WINDOW) for s in SENSORS})
    last = _latest.setdefault(node, {})
    row = {}
    for s in SENSORS:
        v = record.get(s)
        if v is None or pd.isna(v):                 # missing -> previous value
            v = last.get(s, sum(RANGES[s]) / 2)
        lo, hi = RANGES[s]
        v = min(max(float(v), lo), hi)              # clip to range
        prev = last.get(s)
        hist[s].append(v)
        vals = list(hist[s])
        others = [n[s] for k, n in _latest.items() if k != node and s in n]
        row[s] = v
        row[s + "_diff"] = 0.0 if prev is None else v - prev
        row[s + "_roll_mean"] = float(np.mean(vals))
        row[s + "_roll_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        row[s + "_nbr_diff"] = v - float(np.mean(others)) if others else 0.0
        last[s] = v
    return pd.DataFrame([row], columns=FEATURES)

def preprocess(record):
    """Scaled feature row, ready for the model."""
    global _scaler
    if _scaler is None:
        _scaler = joblib.load(os.path.join(HERE, "scaler.joblib"))
    return _scaler.transform(build_features(record))
if __name__ == "__main__":
    prepare_training_data()
    raw = pd.read_csv(os.path.join(HERE, "sensor_data.csv"))
    train_df = add_features(clean(load_data()))
    live_rows = []
    for rec in raw.to_dict("records"):
        f = build_features(rec)
        f["node_id"], f["timestamp"] = rec["node_id"], rec["timestamp"]
        live_rows.append(f)
    live = pd.concat(live_rows).sort_values(["node_id", "timestamp"]).reset_index(drop=True)
    cols = [c for c in FEATURES if not c.endswith("_nbr_diff")]
    print("Live matches training:", np.allclose(live[cols].values, train_df[cols].values, atol=1e-4))
    print(preprocess(raw.iloc[0].to_dict()).shape)