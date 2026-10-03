"""
EML Blockchain Model - real-time pipeline (Person B)

Flow for every reading:
    generate reading -> process_reading() -> add to blockchain -> verify record

process_reading() below is a PLACEHOLDER. When Person A finishes the real
model and trust score, replace it with their function (same input/output).
"""

import os
import random
import sys
import time

# let this file import blockchain.py from the ../blockchain folder
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blockchain"))
from blockchain import Blockchain  # noqa: E402

NODES = ["N01", "N02", "N03", "N04", "N05"]


# ---------------- dummy data generator (Person A will provide the real one) ----------------
def generate_reading():
    node = random.choice(NODES)
    if random.random() < 0.15:                      # 15% fake readings
        data = {"temperature": round(random.uniform(60, 100), 1),
                "humidity": round(random.uniform(0, 10), 1)}
        label = 1
    else:
        data = {"temperature": round(random.gauss(27, 1.5), 1),
                "humidity": round(random.gauss(60, 4), 1)}
        label = 0
    return {"node_id": node, "sensor_data": data, "label": label}


# ---------------- PLACEHOLDER for Person A's detection + trust score ----------------
_trust = {n: 0.5 for n in NODES}


def process_reading(record):
    t = record["sensor_data"]["temperature"]
    h = record["sensor_data"]["humidity"]
    fake = (t < 15 or t > 40) or (h < 20 or h > 90)
    record["prediction"] = 1 if fake else 0
    record["confidence"] = 0.95
    node = record["node_id"]
    _trust[node] = max(0.0, _trust[node] - 0.15) if fake else min(1.0, _trust[node] + 0.02)
    record["trust_score"] = round(_trust[node], 3)
    return record


# ---------------- the real-time loop ----------------
def run(n_readings=50, delay=0.0):
    bc = Blockchain()
    latencies = []
    flagged = 0
    tampered = 0

    for _ in range(n_readings):
        start = time.perf_counter()

        record = process_reading(generate_reading())
        block = bc.add_block(record["node_id"], record["sensor_data"],
                             record["prediction"], record["confidence"],
                             record["trust_score"], label=record["label"])
        status = bc.verify_record(block.index)

        latencies.append((time.perf_counter() - start) * 1000)   # ms
        flagged += record["prediction"]
        tampered += status != "VERIFIED"

        print(f"#{block.index:03d} {record['node_id']} "
              f"T={record['sensor_data']['temperature']:5.1f} "
              f"pred={'FAKE' if record['prediction'] else 'ok  '} "
              f"trust={record['trust_score']:.2f} {status}")
        time.sleep(delay)                      # use e.g. 0.5 to see it stream live

    anchor = bc.get_anchor()
    valid, where = bc.verify_chain(anchor)
    bc.save("chain.json")

    print("\n----- Summary -----")
    print("Readings processed :", n_readings)
    print("Flagged as fake    :", flagged)
    print("Tampered records   :", tampered)
    print("Chain valid        :", valid)
    print(f"Avg latency        : {sum(latencies) / len(latencies):.3f} ms per reading")
    print(f"Max latency        : {max(latencies):.3f} ms")


if __name__ == "__main__":
    random.seed(1)
    run(n_readings=30, delay=0.1)