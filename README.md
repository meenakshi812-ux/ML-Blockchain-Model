# EML Blockchain Model

Real-time implementation of the paper "Blockchain-Assisted Machine Learning Framework with Dynamic Trust Scoring for Secure Fake Sensor Data Detection and Tamper-Proof Data Integrity in IoT Networks". Sensor data is simulated.

## How it works
1. 10 virtual sensor nodes generate readings (temperature, humidity, pressure). Some readings are fake (spoof, spike, drift, replay, stuck).
2. Preprocessing cleans each reading and builds features.
3. A Random Forest model predicts genuine or fake.
4. A dynamic trust score is updated for each node.
5. Every record is stored on a hash-linked blockchain (SHA-256).
6. Each record is verified, so any tampering is detected immediately.

## Folders
- `detection/` - data generator, preprocessing, ML model and trust score (Person A)
- `blockchain/` - blockchain with SHA-256 hashing and tamper detection (Person B)
- `pipeline/` - real-time pipeline connecting all stages (Person B)
- `dashboard/` - live Streamlit dashboard (Person B)

## Setup
    pip install -r requirements.txt

## Run
    python blockchain/blockchain.py        (blockchain tamper tests)
    python pipeline/pipeline.py            (real-time pipeline, prints a summary)
    streamlit run dashboard/dashboard.py   (live dashboard with tamper demo)

## Sample result (pipeline, 100 ticks = 1000 readings)
- Detection accuracy: 0.975 (147 of 165 fake readings caught)
- Tampered records: 0, chain valid: True
- Average time per reading: about 9 ms (ML + trust score + blockchain)

## Team
- Person A: data generation, preprocessing, ML model, trust score
- Person B: blockchain, pipeline, dashboard