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
- `screenshots/` - dashboard screenshots

## Setup
    pip install -r requirements.txt

## Run
    python blockchain/blockchain.py        (blockchain tamper tests)
    python pipeline/pipeline.py            (real-time pipeline, prints a summary)
    streamlit run dashboard/dashboard.py   (live dashboard with tamper demo)

## Retrain the model (optional)
    cd detection
    python train_model.py

Note: this overwrites the saved model and graph files in the `detection` folder.

## Dashboard
Normal operation, chain status VALID:

![Dasboard](screenshot/image1.png)

![Dashboard normal](screenshot/image2.png)
![Dashboard normal](screenshot/image3.png)

After a stored record is tampered with, chain status turns TAMPERED and the changed block is flagged:

![Dashboard tampered](screenshot/image4.png)

## Results

### Machine learning (test set, 2000 readings)
| Metric | This work | Paper |
|---|---|---|
| Accuracy | 0.978 | 0.96 |
| Precision | 0.987 | 0.95 |
| Recall | 0.905 | 0.96 |
| F1-score | 0.944 | 0.955 |

### Real-time pipeline (100 ticks = 1000 readings)
- 147 of 165 fake readings detected, detection accuracy 0.975
- Tampered records: 0, chain valid: True
- Average time per reading: about 9 ms (ML + trust score + blockchain)

### Blockchain tamper tests
All 4 attacks detected: edited value, deleted block, reordered blocks, deleted last block.

## Limitations
- Sensor data is simulated, not collected from physical IoT hardware.
- The blockchain runs on a single machine without distributed consensus.

## Team
- Person A: data generation, preprocessing, ML model, trust score
- Person B: blockchain, pipeline, dashboard