"""
EML Blockchain Model - real-time pipeline (Person B)

Flow for every tick (one reading per node):
    sensor network (Person A) -> ML prediction (Person A) -> trust score (Person A)
    -> add to blockchain (Person B) -> verify record (Person B)

Run from the repo folder:
    python pipeline/pipeline.py
"""

import os
import sys
import time
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "blockchain"))
sys.path.insert(0, os.path.join(HERE, "..", "detection"))

from blockchain import Blockchain               # noqa: E402
from data_generator import SensorNetwork        # noqa: E402  (stage 1)
from predict import predict_reading             # noqa: E402  (stages 2 + 3)
import trust_score                              # noqa: E402  (stage 4)

SENSORS = ["temperature", "humidity", "pressure"]


def new_network(seed=None):
    """Fresh sensor network and fresh trust scores."""
    trust_score.reset()
    return SensorNetwork(seed)


def process_tick(net, bc, tick):
    """Run ONE tick: every node sends a reading, which is classified,
    trust-scored, stored on the chain and verified.
    Returns a list of result dicts (one per node)."""
    timestamp = datetime(2026, 1, 1) + timedelta(seconds=tick)
    results = []
    for rec in net.step(timestamp):
        start = time.perf_counter()

        prediction, confidence = predict_reading(rec)                 # ML model
        trust = trust_score.update_trust(rec["node_id"], prediction, confidence)

        sensor_data = {s: rec.get(s) for s in SENSORS}
        block = bc.add_block(rec["node_id"], sensor_data, prediction,
                             round(confidence, 4), trust, label=rec["label"])
        status = bc.verify_record(block.index)

        results.append({
            "block": block.index,
            "node": rec["node_id"],
            **sensor_data,
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "trust": trust,
            "trusted": trust_score.is_trusted(rec["node_id"]),
            "label": rec["label"],
            "attack_type": rec["attack_type"],
            "integrity": status,
            "latency_ms": (time.perf_counter() - start) * 1000,
        })
    return results


def run(n_ticks=50, delay=0.0, seed=7, verbose=True):
    net = new_network(seed)
    bc = Blockchain()
    all_results = []

    for tick in range(n_ticks):
        for r in process_tick(net, bc, tick):
            all_results.append(r)
            if verbose and (r["prediction"] == 1 or r["label"] == 1):
                print(f"#{r['block']:04d} {r['node']} "
                      f"T={r['temperature']} "
                      f"pred={'FAKE' if r['prediction'] else 'ok  '} "
                      f"(true={'FAKE' if r['label'] else 'ok  '}, {r['attack_type']}) "
                      f"trust={r['trust']:.2f} {r['integrity']}")
        time.sleep(delay)

    anchor = bc.get_anchor()
    valid, _ = bc.verify_chain(anchor)
    bc.save("chain.json")

    tp = sum(1 for r in all_results if r["prediction"] == 1 and r["label"] == 1)
    fp = sum(1 for r in all_results if r["prediction"] == 1 and r["label"] == 0)
    fn = sum(1 for r in all_results if r["prediction"] == 0 and r["label"] == 1)
    tn = sum(1 for r in all_results if r["prediction"] == 0 and r["label"] == 0)
    n = len(all_results)
    lat = [r["latency_ms"] for r in all_results]

    print("\n----- Summary -----")
    print("Ticks / readings    :", n_ticks, "/", n)
    print("Fake readings (true):", tp + fn)
    print("Detected as fake    :", tp + fp, f"(correct {tp}, false alarms {fp}, missed {fn})")
    print(f"Detection accuracy  : {(tp + tn) / n:.3f}")
    print("Tampered records    :", sum(r['integrity'] != 'VERIFIED' for r in all_results))
    print("Chain valid         :", valid)
    print(f"Avg latency         : {sum(lat) / n:.3f} ms per reading (ML + trust + blockchain)")
    print(f"Max latency         : {max(lat):.3f} ms")
    return all_results


if __name__ == "__main__":
    run(n_ticks=100)