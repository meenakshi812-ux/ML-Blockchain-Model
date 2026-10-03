# ML Blockchain Model

Real-time implementation of the paper "Blockchain-Assisted Machine Learning Framework with Dynamic Trust Scoring for Secure Fake Sensor Data Detection and Tamper-Proof Data Integrity in IoT Networks". Sensor data is simulated.

## How it works
1. Virtual sensor nodes generate readings (some are fake).
2. A detector predicts genuine or fake and a trust score is updated per node.
3. Every record is stored on a hash-linked blockchain.
4. Records are verified, so any tampering is detected immediately.

## Folders
- `blockchain/` - blockchain with SHA-256 hashing and tamper detection
- `pipeline/` - real-time pipeline connecting all stages
- `dashboard/` - live Streamlit dashboard
- `detection/` - data generation, ML model and trust score (Person A)

## Setup
    pip install streamlit pandas

## Run
    python blockchain/blockchain.py        (tamper tests)
    python pipeline/pipeline.py            (live pipeline)
    streamlit run dashboard/dashboard.py   (dashboard)

## Record format
node_id, timestamp, sensor values, label, prediction, confidence, trust_score, hash, integrity_status

## Team
- Person A: data generation, preprocessing, ML model, trust score
- Person B: blockchain, pipeline, dashboard
