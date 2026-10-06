"""
data_generator.py  -  Task 1: Synthetic real-time sensor data generator

- 10 virtual nodes (N01..N10), one reading per node per tick
- Genuine readings: shared ambient trend + node offset + small noise
- Fake readings (5 types): spoof, spike, drift, replay, stuck
- Hidden label: 0 = genuine, 1 = fake (attack_type kept for analysis only)

!! Edit SENSORS below to match the sensors / ranges used in your paper !!

Usage:
    python data_generator.py            -> writes sensor_data.csv
    from data_generator import live_stream, generate_dataset
"""
import csv
import math
import random
import time
from collections import deque
from datetime import datetime, timedelta

# ----------------------------------------------------------------- CONFIG
NUM_NODES = 10
PERIOD = 600            # ticks for one slow ambient cycle
P_ATTACK_START = 0.012  # chance per tick that a healthy node starts an attack
P_MISSING = 0.003       # chance a genuine sensor value is missing (for Task 2)

# CHANGE THESE to match the paper
SENSORS = {
    "temperature": {"min": 15.0, "max": 40.0, "base": 27.0, "swing": 3.0, "noise": 0.15},
    "humidity":    {"min": 30.0, "max": 90.0, "base": 60.0, "swing": 8.0, "noise": 0.50},
    "pressure":    {"min": 980.0, "max": 1040.0, "base": 1010.0, "swing": 4.0, "noise": 0.30},
}

ATTACKS = {            # type: (min_duration, max_duration)
    "spoof":  (10, 30),   # random values anywhere in range
    "spike":  (3, 8),     # sudden big jump from the true value
    "drift":  (20, 50),   # slowly growing offset
    "replay": (15, 40),   # old genuine values played back
    "stuck":  (15, 40),   # value frozen
}

FIELDS = ["node_id", "timestamp"] + list(SENSORS) + ["label", "attack_type"]


def _clip(v, s):
    return max(SENSORS[s]["min"], min(SENSORS[s]["max"], v))


class Node:
    def __init__(self, node_id, rng):
        self.id = node_id
        self.rng = rng
        self.offset = {s: rng.uniform(-1, 1) * c["swing"] * 0.3 for s, c in SENSORS.items()}
        self.history = {s: deque(maxlen=400) for s in SENSORS}
        self.attack = None  # dict while under attack

    def _start_attack(self):
        kind = self.rng.choice(list(ATTACKS))
        if kind == "replay" and len(self.history[next(iter(SENSORS))]) < 300:
            return  # not enough history yet
        lo, hi = ATTACKS[kind]
        self.attack = {
            "type": kind,
            "left": self.rng.randint(lo, hi),
            "k": 0,
            "lag": self.rng.randint(100, 250),
            "sign": self.rng.choice([-1, 1]),
            "frozen": None,
        }

    def read(self, ambient):
        """Return (values dict, label, attack_type) for this tick."""
        rng = self.rng
        true = {s: _clip(ambient[s] + self.offset[s] + rng.gauss(0, c["noise"]), s)
                for s, c in SENSORS.items()}

        if self.attack is None and rng.random() < P_ATTACK_START:
            self._start_attack()

        values, label, kind = dict(true), 0, "none"
        a = self.attack
        if a:
            label, kind = 1, a["type"]
            for s, c in SENSORS.items():
                rngv = c["max"] - c["min"]
                if kind == "spoof":
                    values[s] = rng.uniform(c["min"], c["max"])
                elif kind == "spike":
                    values[s] = _clip(true[s] + a["sign"] * rng.uniform(0.25, 0.45) * rngv, s)
                elif kind == "drift":
                    values[s] = _clip(true[s] + a["sign"] * 0.01 * rngv * (a["k"] + 1), s)
                elif kind == "replay":
                    values[s] = self.history[s][-a["lag"]]
                elif kind == "stuck":
                    if a["frozen"] is None:
                        a["frozen"] = dict(true)
                    values[s] = a["frozen"][s]
            a["k"] += 1
            a["left"] -= 1
            if a["left"] <= 0:
                self.attack = None
        else:
            # occasionally drop a value (genuine data only) to test cleaning
            if rng.random() < P_MISSING:
                values[rng.choice(list(SENSORS))] = None

        for s in SENSORS:           # history always stores the TRUE values
            self.history[s].append(true[s])
        return values, label, kind


class SensorNetwork:
    def __init__(self, seed=None, num_nodes=NUM_NODES):
        self.rng = random.Random(seed)
        self.nodes = [Node(f"N{i+1:02d}", self.rng) for i in range(num_nodes)]
        self.t = 0
        self.walk = {s: 0.0 for s in SENSORS}   # shared slow random walk

    def _ambient(self):
        amb = {}
        for s, c in SENSORS.items():
            self.walk[s] = 0.995 * self.walk[s] + self.rng.gauss(0, c["noise"] * 0.2)
            amb[s] = c["base"] + c["swing"] * math.sin(2 * math.pi * self.t / PERIOD) + self.walk[s]
        return amb

    def step(self, timestamp):
        amb = self._ambient()
        records = []
        for n in self.nodes:
            vals, label, kind = n.read(amb)
            rec = {"node_id": n.id, "timestamp": timestamp.isoformat(timespec="seconds")}
            rec.update({s: (None if v is None else round(v, 2)) for s, v in vals.items()})
            rec.update({"label": label, "attack_type": kind})
            records.append(rec)
        self.t += 1
        return records


def generate_dataset(n_steps=1000, path="sensor_data.csv", seed=42):
    """Historical dataset for training (1000 steps x 10 nodes = 10,000 rows)."""
    net = SensorNetwork(seed)
    start = datetime(2026, 1, 1)
    fake = total = 0
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i in range(n_steps):
            for rec in net.step(start + timedelta(seconds=i)):
                w.writerow(rec)
                fake += rec["label"]
                total += 1
    print(f"Saved {total} rows to {path}  |  fake = {fake} ({100*fake/total:.1f}%)")


def live_stream(interval=1.0, seed=None):
    """Generator: yields one list of records (one per node) every `interval` s."""
    net = SensorNetwork(seed)
    while True:
        yield net.step(datetime.now())
        time.sleep(interval)


if __name__ == "__main__":
    generate_dataset()
