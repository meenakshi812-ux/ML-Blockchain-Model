import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)
from preprocessing import prepare_training_data

X_train, X_test, y_train, y_test = prepare_training_data()

# Random Forest with the paper's parameters
model = RandomForestClassifier(n_estimators=100, max_depth=10, criterion="gini",
                               random_state=42)

# 5-fold cross-validation on the training set
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1")
print("CV F1 per fold:", scores.round(3))
print("CV F1 mean: %.3f (+/- %.3f)" % (scores.mean(), scores.std()))

# Train on the full training set and test
model.fit(X_train, y_train)
pred = model.predict(X_test)

print("\nTest results")
print("Accuracy :", round(accuracy_score(y_test, pred), 3))
print("Precision:", round(precision_score(y_test, pred), 3))
print("Recall   :", round(recall_score(y_test, pred), 3))
print("F1-score :", round(f1_score(y_test, pred), 3))
print("Confusion matrix:\n", confusion_matrix(y_test, pred))

joblib.dump(model, "model.joblib")
print("\nSaved model.joblib")
# ---------------- GRAPHS ----------------
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from preprocessing import FEATURES

# 1. Confusion matrix
ConfusionMatrixDisplay.from_predictions(
    y_test, pred, display_labels=["Genuine", "Fake"], cmap="Blues")
plt.title("Confusion Matrix (Random Forest)")
plt.savefig("confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()

# 2. Metric comparison: our result vs the paper
names = ["Accuracy", "Precision", "Recall", "F1-score"]
ours = [accuracy_score(y_test, pred), precision_score(y_test, pred),
        recall_score(y_test, pred), f1_score(y_test, pred)]
paper = [0.96, 0.95, 0.96, 0.955]
x = range(len(names))
plt.bar([i - 0.2 for i in x], paper, width=0.4, label="Paper")
plt.bar([i + 0.2 for i in x], ours, width=0.4, label="This work")
plt.xticks(list(x), names)
plt.ylim(0.8, 1.0)
plt.ylabel("Score")
plt.title("Metric Comparison")
plt.legend()
plt.savefig("metric_comparison.png", dpi=150, bbox_inches="tight")
plt.close()

# 3. Feature importance
imp = sorted(zip(model.feature_importances_, FEATURES), reverse=True)
print("\nTop 5 important features:")
for score, name in imp[:5]:
    print(" ", name, round(score, 3))
print("Saved confusion_matrix.png and metric_comparison.png")