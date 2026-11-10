
import csv
import joblib
from pathlib import Path

from audio_features import extract_features

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

# ==========================================
# 1. PATHS
# ==========================================

BASE_DIR = Path(r"C:\Users\7905n\Downloads\LA\LA")

AUDIO_DIR = BASE_DIR / "ASVspoof2019_LA_eval" / "flac"

PROTOCOL = (
    BASE_DIR
    / "ASVspoof2019_LA_cm_protocols"
    / "ASVspoof2019.LA.cm.eval.trl.txt"
)

MODEL_PATH = Path("models/voice_detector.joblib")

OUTPUT_CSV = Path("evaluation_predictions.csv")

# ==========================================
# 2. LOAD MODEL
# ==========================================

print("Loading Logistic Regression model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")

# ==========================================
# 3. READ EVALUATION PROTOCOL
# ==========================================

print("\nReading evaluation protocol...")

test_files = []

with open(PROTOCOL, "r") as file:
    for line in file:
        parts = line.strip().split()

        if len(parts) < 5:
            continue

        filename = parts[1]
        label = parts[-1]

        audio_path = AUDIO_DIR / f"{filename}.flac"

        if label == "bonafide":
            actual_label = 0
        elif label == "spoof":
            actual_label = 1
        else:
            continue

        test_files.append((audio_path, actual_label))

print("Total recordings:", len(test_files))

print(
    "Genuine recordings:",
    sum(1 for _, label in test_files if label == 0)
)

print(
    "Spoof recordings:",
    sum(1 for _, label in test_files if label == 1)
)

# ==========================================
# 4. VERIFY AUDIO FILES
# ==========================================

missing_files = [
    str(path)
    for path, _ in test_files
    if not path.exists()
]

if missing_files:
    print("\nMissing audio files:", len(missing_files))
    print("First missing file:", missing_files[0])
    raise FileNotFoundError(
        "Some evaluation audio files are missing. Check the dataset."
    )

print("\nAll audio files found.")

# ==========================================
# 5. EXTRACT FEATURES AND PREDICT
# ==========================================

y_true = []
y_pred = []

errors = 0

print("\nStarting evaluation...")
print("This may take several hours. Do not close the terminal.")

with open(OUTPUT_CSV, "w", newline="") as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "Filename",
        "Actual",
        "Predicted",
        "Bonafide_Score",
        "Spoof_Score",
        "Correct"
    ])

    for index, (audio_path, actual_label) in enumerate(
        test_files, 1
    ):

        try:
            features = extract_features(
                str(audio_path)
            ).reshape(1, -1)

            prediction = int(model.predict(features)[0])

            probabilities = model.predict_proba(features)[0]

            bonafide_score = float(probabilities[0])
            spoof_score = float(probabilities[1])

            y_true.append(actual_label)
            y_pred.append(prediction)

            actual_name = (
                "BONAFIDE" if actual_label == 0 else "SPOOF"
            )

            predicted_name = (
                "BONAFIDE" if prediction == 0 else "SPOOF"
            )

            writer.writerow([
                audio_path.name,
                actual_name,
                predicted_name,
                round(bonafide_score, 6),
                round(spoof_score, 6),
                actual_label == prediction
            ])

        except Exception as error:
            errors += 1
            print(
                f"\nError processing {audio_path.name}: {error}"
            )

        if index % 500 == 0:
            print(
                f"Processed {index}/{len(test_files)} "
                f"| Successful: {len(y_true)} "
                f"| Errors: {errors}"
            )

# ==========================================
# 6. FINAL EVALUATION
# ==========================================

print("\n" + "=" * 60)
print("ASVSPOOF2019 EVALUATION RESULTS")
print("=" * 60)

print("Total recordings:", len(test_files))
print("Successfully evaluated:", len(y_true))
print("Failed recordings:", errors)

if not y_true:
    print("No recordings were successfully evaluated.")
    raise SystemExit

print(
    "\nAccuracy:",
    round(accuracy_score(y_true, y_pred) * 100, 2),
    "%"
)

print(
    "Balanced Accuracy:",
    round(balanced_accuracy_score(y_true, y_pred) * 100, 2),
    "%"
)

print(
    "Macro Precision:",
    round(
        precision_score(
            y_true, y_pred,
            average="macro",
            zero_division=0
        ) * 100, 2
    ),
    "%"
)

print(
    "Macro Recall:",
    round(
        recall_score(
            y_true, y_pred,
            average="macro",
            zero_division=0
        ) * 100, 2
    ),
    "%"
)

print(
    "Macro F1:",
    round(
        f1_score(
            y_true, y_pred,
            average="macro",
            zero_division=0
        ) * 100, 2
    ),
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

print(
    confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )
)

print("\nPredictions saved to:", OUTPUT_CSV)
print("\nEvaluation completed!")
