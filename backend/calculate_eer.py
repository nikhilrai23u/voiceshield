
import csv
import numpy as np
from sklearn.metrics import roc_curve

y_true = []
spoof_scores = []

with open("evaluation_predictions.csv", "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        actual = 1 if row["Actual"] == "SPOOF" else 0

        y_true.append(actual)
        spoof_scores.append(float(row["Spoof_Score"]))

fpr, tpr, thresholds = roc_curve(
    y_true,
    spoof_scores,
    pos_label=1
)

fnr = 1 - tpr

index = np.nanargmin(np.abs(fpr - fnr))

eer = (fpr[index] + fnr[index]) / 2

print("\nVOICE SHIELD — EER RESULTS")
print("=" * 40)

print(f"EER: {eer * 100:.2f}%")
print(f"False Positive Rate: {fpr[index] * 100:.2f}%")
print(f"False Negative Rate: {fnr[index] * 100:.2f}%")
print(f"Threshold: {thresholds[index]:.6f}")
