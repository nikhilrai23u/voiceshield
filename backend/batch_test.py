
import joblib
import random
from pathlib import Path
from collections import Counter

from audio_features import extract_features
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)

# ==========================================
# 1. PATHS AND MODEL
# ==========================================

BASE_DIR = Path(r"C:\Users\7905n\Downloads\LA\LA")

AUDIO_DIR = BASE_DIR / "ASVspoof2019_LA_dev" / "flac"

PROTOCOL = (
    BASE_DIR
    / "ASVspoof2019_LA_cm_protocols"
    / "ASVspoof2019.LA.cm.dev.trl.txt"
)

model = joblib.load("models/voice_detector.joblib")

# ==========================================
# 2. READ GENUINE AND SPOOF FILES
# ==========================================

genuine_files = []
spoof_files = []

with open(PROTOCOL, "r") as f:
    for line in f:
        parts = line.strip().split()

        if len(parts) < 5:
            continue

        filename = parts[1]
        label = parts[-1]

        audio_path = AUDIO_DIR / f"{filename}.flac"

        if not audio_path.exists():
            continue

        if label == "bonafide":
            genuine_files.append(audio_path)

        elif label == "spoof":
            spoof_files.append(audio_path)

print("Available genuine files:", len(genuine_files))
print("Available spoof files:", len(spoof_files))

# ==========================================
# 3. SELECT 10 FROM EACH CLASS
# ==========================================

random.seed(42)

selected_genuine = random.sample(genuine_files, 10)
selected_spoof = random.sample(spoof_files, 10)

test_files = []

for path in selected_genuine:
    test_files.append((path, 0))

for path in selected_spoof:
    test_files.append((path, 1))

# ==========================================
# 4. EXTRACT FEATURES AND PREDICT
# ==========================================

y_true = []
y_pred = []

for index, (path, actual_label) in enumerate(test_files, 1):

    print(f"\nTesting {index}/20: {path.name}")

    try:
        features = extract_features(str(path)).reshape(1, -1)

        prediction = int(model.predict(features)[0])

        y_true.append(actual_label)
        y_pred.append(prediction)

        actual = "BONAFIDE" if actual_label == 0 else "SPOOF"
        predicted = "BONAFIDE" if prediction == 0 else "SPOOF"

        print("Actual:", actual)
        print("Predicted:", predicted)
        print("Result:", "CORRECT" if actual_label == prediction else "WRONG")

    except Exception as error:
        print("ERROR:", error)

# ==========================================
# 5. EVALUATION
# ==========================================

print("\n" + "=" * 55)
print("BATCH TEST RESULTS")
print("=" * 55)

if len(y_true) > 0:
    print("Successful tests:", len(y_true))
    print("Accuracy:", round(accuracy_score(y_true, y_pred) * 100, 2), "%")
    print(
        "Balanced Accuracy:",
        round(balanced_accuracy_score(y_true, y_pred) * 100, 2),
        "%"
    )

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["BONAFIDE", "SPOOF"],
            zero_division=0
        )
    )

    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1]))

else:
    print("No recordings could be tested.")
