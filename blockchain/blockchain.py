"""
EML Blockchain Model - blockchain module (Person B)

Stores every sensor record (with the ML prediction and trust score) in a
hash-linked chain, and detects tampering.
"""

import copy
import hashlib
import json
import time


class Block:
    def __init__(self, index, node_id, sensor_data, prediction, confidence,
                 trust_score, previous_hash, label=None, timestamp=None):
        self.index = index
        self.node_id = node_id              # e.g. "N01"
        self.sensor_data = sensor_data      # dict, e.g. {"temperature": 27.4}
        self.prediction = prediction        # 0 = genuine, 1 = fake
        self.confidence = confidence        # model probability, 0..1
        self.trust_score = trust_score      # node trust score, 0..1
        self.label = label                  # ground truth (for evaluation only)
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        content = {
            "index": self.index,
            "node_id": self.node_id,
            "sensor_data": self.sensor_data,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "trust_score": self.trust_score,
            "label": self.label,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
        }
        encoded = json.dumps(content, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        block = cls.__new__(cls)       # keep the stored hash, do not recompute
        block.__dict__.update(d)
        return block


class Blockchain:
    def __init__(self):
        self.chain = [self._genesis_block()]

    @staticmethod
    def _genesis_block():
        return Block(0, "GENESIS", {}, 0, 1.0, 1.0, "0", timestamp=0)

    def add_block(self, node_id, sensor_data, prediction, confidence,
                  trust_score, label=None):
        prev = self.chain[-1]
        block = Block(len(self.chain), node_id, sensor_data, prediction,
                      confidence, trust_score, prev.hash, label=label)
        self.chain.append(block)
        return block

    def get_anchor(self):
        """Chain length + latest hash. Keep this somewhere separate
        (e.g. a different file) so deleting the LAST block can be detected."""
        return len(self.chain), self.chain[-1].hash

    def verify_chain(self, anchor=None):
        """Returns (True, None) if valid, else (False, reason/index)."""
        genesis = self.chain[0]
        if genesis.hash != genesis.compute_hash():
            return False, 0
        for i in range(1, len(self.chain)):
            cur, prev = self.chain[i], self.chain[i - 1]
            if cur.index != i:
                return False, i              # block removed or reordered
            if cur.hash != cur.compute_hash():
                return False, i              # block content was altered
            if cur.previous_hash != prev.hash:
                return False, i              # link to previous block broken
        if anchor is not None:
            length, last_hash = anchor
            if len(self.chain) != length or self.chain[-1].hash != last_hash:
                return False, "chain shorter/different than anchor"
        return True, None

    def verify_record(self, index):
        """Check one stored record. Returns 'VERIFIED' or 'TAMPERED'."""
        if index < 0 or index >= len(self.chain):
            return "TAMPERED"
        block = self.chain[index]
        if block.hash != block.compute_hash():
            return "TAMPERED"
        if index > 0 and block.previous_hash != self.chain[index - 1].hash:
            return "TAMPERED"
        return "VERIFIED"

    def save(self, path="chain.json"):
        with open(path, "w") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    @classmethod
    def load(cls, path="chain.json"):
        with open(path) as f:
            data = json.load(f)
        bc = cls.__new__(cls)
        bc.chain = [Block.from_dict(d) for d in data]
        return bc


def build_demo_chain():
    bc = Blockchain()
    bc.add_block("N01", {"temperature": 27.4, "humidity": 60}, 0, 0.97, 0.92, label=0)
    bc.add_block("N02", {"temperature": 28.1, "humidity": 58}, 0, 0.95, 0.85, label=0)
    bc.add_block("N03", {"temperature": 26.9, "humidity": 62}, 0, 0.91, 0.78, label=0)
    bc.add_block("N04", {"temperature": 75.0, "humidity": 5}, 1, 0.99, 0.20, label=1)
    return bc


if __name__ == "__main__":
    # ---- Test 0: untouched chain ----
    bc = build_demo_chain()
    anchor = bc.get_anchor()
    print("Test 0 - untouched chain      :", bc.verify_chain(anchor))
    print("         record 2 status      :", bc.verify_record(2))

    # ---- Test 1: edit a stored value ----
    t = copy.deepcopy(bc)
    t.chain[2].sensor_data["temperature"] = 99.9
    print("Test 1 - edited value         :", t.verify_chain(anchor),
          "| record 2:", t.verify_record(2))

    # ---- Test 2: delete a block in the middle ----
    t = copy.deepcopy(bc)
    del t.chain[2]
    print("Test 2 - deleted middle block :", t.verify_chain(anchor))

    # ---- Test 3: reorder two blocks ----
    t = copy.deepcopy(bc)
    t.chain[1], t.chain[2] = t.chain[2], t.chain[1]
    print("Test 3 - reordered blocks     :", t.verify_chain(anchor))

    # ---- Test 4: delete the LAST block (needs the anchor) ----
    t = copy.deepcopy(bc)
    t.chain.pop()
    print("Test 4 - deleted last block   :", t.verify_chain(anchor),
          "(without anchor:", t.verify_chain(), ")")

    # ---- Test 5: save and load ----
    bc.save("chain.json")
    loaded = Blockchain.load("chain.json")
    print("Test 5 - save/load            :", loaded.verify_chain(anchor))