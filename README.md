# ML - BLOCKCHAIN MODEL

Real-time implementation of the IEEE paper "Blockchain-Assisted Machine Learning Framework with Dynamic Trust Scoring for Secure Fake Sensor Data Detection and Tamper-Proof Data Integrity in IoT Networks". Sensor data is simulated.

## PUBLICATION
This project is the real-time implementation of the paper:

**"Blockchain-Assisted Machine Learning Framework with Dynamic Trust Scoring for Secure Fake Sensor Data Detection and Tamper-Proof Data Integrity in IoT Networks"**

- Authors: S.Meenakshi , K.Priyadharshini , S.Vignesh devi , Dr.J.V.Anchitaalagammai, Dr.S.Kavitha , Mr.S.Murali
- Conference: ICOSICS International Conference on Secure IoT and Cybersecurity 2026
- Publisher: IEEE Xplore
- Status: [Accepted and Presented IEEE Xplore]

## HOW IT WORKS 
1. 10 virtual sensor nodes generate readings (temperature, humidity, pressure). Some readings are fake (spoof, spike, drift, replay, stuck).
2. Preprocessing cleans each reading and builds features.
3. A Random Forest model predicts genuine or fake.
4. A dynamic trust score is updated for each node.
5. Every record is stored on a hash-linked blockchain (SHA-256).
6. Each record is verified, so any tampering is detected immediately.

## WORKFLOW
Sensors → Preprocessing → Random Forest → Trust score → Blockchain → Verification → Dashboard


## FOLDERS
- `detection/` - data generator, preprocessing, ML model and trust score (Person A)
- `blockchain/` - blockchain with SHA-256 hashing and tamper detection (Person B)
- `pipeline/` - real-time pipeline connecting all stages (Person B)
- `dashboard/` - live Streamlit dashboard (Person B)
- `screenshot/` - dashboard screenshots

## SETUP
    pip install -r requirements.txt

## RUN
    python blockchain/blockchain.py        (blockchain tamper tests)
    python pipeline/pipeline.py            (real-time pipeline, prints a summary)
    streamlit run dashboard/dashboard.py   (live dashboard with tamper demo)

## RETRAIN THE MODEL (Optional)
    cd detection
    python train_model.py

Note: This overwrites the saved model and graph files in the `detection` folder.


## DASHBOARD

### Normal operation (chain status VALID)

![Dashboard summary](screenshot/image1.png)
![Dashboard normal data](screenshot/image2.png)
![Dashboard normal data](screenshot/image3.png)

### After tampering (chain status TAMPERED)
After a stored record is tampered with, the chain status turns TAMPERED and the changed block is flagged:

![Dashboard tampered](screenshot/image4.png)


## RESULTS

### MACHINE LEARNING (test set, 2000 readings)
| Metrics | This work | Paper |
|---|---|---|
| Accuracy | 0.978 | 0.96 |
| Precision | 0.987 | 0.95 |
| Recall | 0.905 | 0.96 |
| F1-score | 0.944 | 0.955 |

### REAL TIME PIPELINE (100 ticks = 1000 readings)
- 147 of 165 fake readings detected, detection accuracy 0.975
- Tampered records: 0, chain valid: True
- Average time per reading: about 9 ms (ML + trust score + blockchain)

### BLOCKCHAIN TAMPER TESTS
All 4 attacks detected: edited value, deleted block, reordered blocks, deleted last block.

## LIMITATIONS
- Sensor data is simulated, not collected from physical IoT hardware.
- The blockchain runs on a single machine without distributed consensus.
- Recall (0.905) is lower than the paper's (0.96)
- F1 score (0.944) is lower than paper's (0.955)


## FUTURE WORK 
- Test the system on a real IoT testbed with physical sensors instead of simulated data.
- Replace the single-machine blockchain with a distributed platform (for example Ethereum or Hyperledger) with consensus.
- Improve recall on subtle attacks by testing other models and more features.
- Add continuous online learning so the model adapts to new attack patterns.

## TEAM
- Person A: Data collection, Preprocessing, ML model, Dynamic Trust score
- Person B: Blockchain, Pipeline, Dashboard

## CONTRIBUTORS
PRIYADHARSHINI K
As person A , I developed the detection side of the system. She built the sensor data generator that simulates 10 virtual nodes producing temperature, humidity and pressure readings, including fake readings from spoof, spike, drift, replay and stuck-value attacks. She implemented the preprocessing and feature-engineering steps, trained and evaluated the Random Forest model that classifies each reading as genuine or fake, and designed the dynamic trust score that updates for each sensor node based on its behaviour.

MEENAKSHI S
As person B , She developed the integrity and delivery side of the system. She implemented the hash-linked blockchain using SHA-256, storing each record with its prediction and trust score, and added chain verification that detects tampering such as edited values and broken links. She built the real-time pipeline that connects sensing, ML detection, trust scoring, blockchain storage and verification, and created the live Streamlit dashboard with a tamper demonstration that flags the altered block.

## FACULTY GUIDES
