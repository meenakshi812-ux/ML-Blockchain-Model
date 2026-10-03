"""
EML Blockchain Model - live dashboard (Person B)

Run from the repo folder with:
    streamlit run dashboard/dashboard.py
"""

import os
import sys
import time

import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "blockchain"))
sys.path.insert(0, os.path.join(HERE, "..", "pipeline"))

from blockchain import Blockchain  # noqa: E402
import pipeline as pl              # noqa: E402

st.set_page_config(page_title="EML Blockchain Model", layout="wide")
st.title("EML Blockchain Model - Live Monitor")
st.caption("Fake sensor data detection with dynamic trust scores and a tamper-proof blockchain")

UNTRUSTED_BELOW = 0.30


def reset():
    st.session_state.bc = Blockchain()
    st.session_state.anchor = st.session_state.bc.get_anchor()
    st.session_state.rows = []
    st.session_state.latencies = []
    for n in pl.NODES:
        pl._trust[n] = 0.5


def add_readings(n):
    bc = st.session_state.bc
    for _ in range(n):
        start = time.perf_counter()
        rec = pl.process_reading(pl.generate_reading())
        block = bc.add_block(rec["node_id"], rec["sensor_data"], rec["prediction"],
                             rec["confidence"], rec["trust_score"], label=rec["label"])
        st.session_state.latencies.append((time.perf_counter() - start) * 1000)
        st.session_state.rows.append({
            "block": block.index,
            "node": rec["node_id"],
            "temperature": rec["sensor_data"]["temperature"],
            "humidity": rec["sensor_data"]["humidity"],
            "prediction": "FAKE" if rec["prediction"] else "ok",
            "trust": rec["trust_score"],
        })
    st.session_state.anchor = bc.get_anchor()   # legitimate additions update the anchor


if "bc" not in st.session_state:
    reset()

bc = st.session_state.bc

# ---------------- sidebar controls ----------------
st.sidebar.header("Controls")
n = st.sidebar.slider("Readings to generate", 1, 100, 20)
if st.sidebar.button("Generate readings", type="primary"):
    add_readings(n)

st.sidebar.markdown("---")
st.sidebar.subheader("Tamper demo")
if len(bc.chain) > 1:
    target = st.sidebar.number_input("Block to tamper with", 1, len(bc.chain) - 1,
                                     len(bc.chain) - 1, step=1)
    if st.sidebar.button("Tamper with this block"):
        bc.chain[int(target)].sensor_data["temperature"] = 99.9
        st.sidebar.warning(f"Block {int(target)} temperature changed to 99.9")
else:
    st.sidebar.info("Generate some readings first.")

st.sidebar.markdown("---")
if st.sidebar.button("Reset everything"):
    reset()
    st.rerun()

# ---------------- main view ----------------
rows = st.session_state.rows
valid, where = bc.verify_chain(st.session_state.anchor)
lat = st.session_state.latencies
flagged = sum(1 for r in rows if r["prediction"] == "FAKE")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Blocks on chain", len(bc.chain) - 1)
c2.metric("Fake readings flagged", flagged)
c3.metric("Chain status", "VALID" if valid else "TAMPERED")
c4.metric("Avg latency", f"{sum(lat) / len(lat):.3f} ms" if lat else "-")

if not valid:
    st.error(f"Tampering detected. First problem found at: {where}")
else:
    st.success("Blockchain verified: no tampering detected.")

if not rows:
    st.info("Click 'Generate readings' in the sidebar to start.")
else:
    left, right = st.columns([3, 2])

    with left:
        st.subheader("Latest records")
        df = pd.DataFrame(rows)
        df["integrity"] = [bc.verify_record(i) for i in df["block"]]
        st.dataframe(df.tail(20).iloc[::-1], hide_index=True)

    with right:
        st.subheader("Trust score per node")
        trust = df.pivot(index="block", columns="node", values="trust").ffill()
        st.line_chart(trust)

        st.subheader("Alerts")
        latest = df.groupby("node")["trust"].last()
        bad = latest[latest < UNTRUSTED_BELOW]
        if bad.empty:
            st.write("No untrusted nodes.")
        for node, score in bad.items():
            st.warning(f"Node {node} is untrusted (trust {score:.2f})")
        if (df["integrity"] == "TAMPERED").any():
            blocks = df.loc[df["integrity"] == "TAMPERED", "block"].tolist()
            st.error(f"Tampered blocks: {blocks}")