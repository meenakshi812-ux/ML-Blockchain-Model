ALPHA = 0.05      # reward for a genuine reading (paper)
BETA = 0.10       # penalty for a fake reading (paper)
THETA = 0.3       # trust threshold (paper)
START = 0.5       # starting trust score

_trust = {}

def update_trust(node_id, prediction, confidence=1.0):
    """Update and return the node's trust score (0 to 1).
    Like the paper, the score ignores the confidence value."""
    t = _trust.get(node_id, START)
    t = t + ALPHA if prediction == 0 else t - BETA
    t = round(min(1.0, max(0.0, t)), 4)
    _trust[node_id] = t
    return t

def is_trusted(node_id):
    """False when the node's score is below the threshold."""
    return _trust.get(node_id, START) >= THETA

def reset():
    _trust.clear()

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    normal, bad = [], []
    for i in range(60):
        normal.append(update_trust("NORMAL", 0))
        # bad node: genuine for 15, attacked for 10, genuine again
        attacked = 15 <= i < 25
        bad.append(update_trust("BAD", 1 if attacked else 0))
        if i in (14, 17, 24, 59):
            print("reading", i + 1, "| normal:", normal[-1],
                  "| bad:", bad[-1], "| bad trusted:", is_trusted("BAD"))

    plt.plot(normal, label="Normal node", color="green")
    plt.plot(bad, label="Attacked node", color="red")
    plt.axhline(THETA, linestyle="--", color="gray", label="Threshold (0.3)")
    plt.xlabel("Reading number")
    plt.ylabel("Trust score")
    plt.ylim(0, 1.05)
    plt.title("Trust Score: Normal vs Attacked Node")
    plt.legend()
    plt.savefig("trust_score.png", dpi=150, bbox_inches="tight")
    print("Saved trust_score.png")
    