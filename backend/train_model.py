
from pathlib import Path
import csv
import numpy as np
import joblib

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from audio_features import extract_features


# ==========================================
# DATASET LOCATIONS
# ==========================================

DATASET_ROOT = Path(r"C:\Users\7905n\Downloads\LA\LA")

TRAIN_PROTOCOL = (
    DATASET_ROOT / "ASVspoof2019_LA_cm_protocols"
    / "ASVspoof2019.LA.cm.train.trn.txt"
)

TRAIN_AUDIO = DATASET_ROOT / "ASVspoof2019_LA_train" / "flac"

DEV_PROTOCOL = (
    DATASET_ROOT / "ASVspoof2019_LA_cm_protocols"
    / "ASVspoof2019.LA.cm.dev.trl.txt"
)

DEV_AUDIO = DATASET_ROOT / "ASVspoof2019_LA_dev" / "flac"


# ==========================================
# MODEL LOCATIONS
# ==========================================

MODEL_DIR = Path("models")

# Existing production model - DO NOT OVERWRITE
CURRENT_MODEL_PATH = MODEL_DIR / "voice_detector.joblib"

# Previous experimental model - DO NOT OVERWRITE
PREVIOUS_CANDIDATE_PATH = (
    MODEL_DIR / "voice_detector_candidate.joblib"
)

# New 30-feature experimental model
CANDIDATE_MODEL_PATH = (
    MODEL_DIR / "voice_detector_30features_candidate.joblib"
)

REPORT_PATH = Path("model_evaluation_report_30features.csv")


# ==========================================
# LOAD DATASET AND EXTRACT FEATURES
# ==========================================

def load_dataset(protocol_path, audio_dir):

    features = []
    labels = []

    rows = protocol_path.read_text().splitlines()

    for index, row in enumerate(rows, start=1):

        fields = row.split()

        if len(fields) < 5:
            continue

        audio_id = fields[1]
        label = fields[-1]

        audio_path = audio_dir / f"{audio_id}.flac"

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        feature_vector = extract_features(str(audio_path))

        features.append(feature_vector)

        # 0 = Genuine voice
        # 1 = Spoofed voice
        if label == "bonafide":
            labels.append(0)
        elif label == "spoof":
            labels.append(1)
        else:
            raise ValueError(f"Unknown label: {label}")

        if index % 100 == 0:
            print(
                f"Processed {index}/{len(rows)} "
                f"from {protocol_path.name}"
            )

    X = np.asarray(features)
    y = np.asarray(labels)

    return X, y


# ==========================================
# MAIN TRAINING FUNCTION
# ==========================================

def main():

    print("=" * 60)
    print("VOICESHIELD - 30 FEATURE MODEL EXPERIMENT")
    print("=" * 60)

    # ======================================
    # LOAD TRAINING DATA
    # ======================================

    print("\nLoading training dataset...")

    X_train, y_train = load_dataset(
        TRAIN_PROTOCOL,
        TRAIN_AUDIO
    )

    print("\nTraining dataset shape:", X_train.shape)

    # ======================================
    # LOAD DEVELOPMENT DATA
    # ======================================

    print("\nLoading development dataset...")

    X_dev, y_dev = load_dataset(
        DEV_PROTOCOL,
        DEV_AUDIO
    )

    print("\nDevelopment dataset shape:", X_dev.shape)

    print("\nDataset loading completed.")

    # Verify feature dimensions
    if X_train.shape[1] != 30 or X_dev.shape[1] != 30:
        raise ValueError(
            "Expected 30 features per recording."
        )

    print("\nFeature verification successful: 30 features.")

    # ======================================
    # DEFINE MODELS
    # ======================================

    models = {

        "Logistic Regression": make_pipeline(
            StandardScaler(),

            LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
            ),
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),

        "SVM": make_pipeline(
            StandardScaler(),

            SVC(
                kernel="rbf",
                class_weight="balanced",
                probability=True,
                random_state=42,
            ),
        ),
    }

    # ======================================
    # TRAIN AND EVALUATE MODELS
    # ======================================

    results = []
    evaluation_rows = []

    best_model = None
    best_score = -1
    best_name = ""

    for name, model in models.items():

        print("\n" + "=" * 60)
        print(f"TRAINING: {name}")
        print("=" * 60)

        model.fit(X_train, y_train)

        print(f"\nEvaluating {name}...")

        predictions = model.predict(X_dev)

        accuracy = accuracy_score(
            y_dev,
            predictions
        )

        balanced_accuracy = balanced_accuracy_score(
            y_dev,
            predictions
        )

        precision = precision_score(
            y_dev,
            predictions,
            average="macro",
            zero_division=0
        )

        recall = recall_score(
            y_dev,
            predictions,
            average="macro",
            zero_division=0
        )

        f1 = f1_score(
            y_dev,
            predictions,
            average="macro",
            zero_division=0
        )

        # Save metrics
        evaluation_rows.append({
            "Model": name,
            "Accuracy": accuracy,
            "Balanced Accuracy": balanced_accuracy,
            "Macro Precision": precision,
            "Macro Recall": recall,
            "Macro F1": f1,
        })

        score = balanced_accuracy

        print("\nAccuracy:")
        print(f"{accuracy * 100:.2f}%")

        print("\nBalanced accuracy:")
        print(f"{balanced_accuracy * 100:.2f}%")

        print("\nClassification report:")

        print(
            classification_report(
                y_dev,
                predictions,
                labels=[0, 1],
                target_names=["BONAFIDE", "SPOOF"],
                zero_division=0,
            )
        )

        print("\nConfusion matrix:")

        print(
            confusion_matrix(
                y_dev,
                predictions,
                labels=[0, 1]
            )
        )

        results.append((name, score))

        # Select best model by balanced accuracy
        if score > best_score:

            best_score = score
            best_model = model
            best_name = name

    # ======================================
    # FINAL MODEL COMPARISON
    # ======================================

    print("\n" + "=" * 60)
    print("30 FEATURE MODEL COMPARISON")
    print("=" * 60)

    for name, score in results:

        print(f"{name}: {score * 100:.2f}%")

    print("\nBest model:", best_name)

    print(
        "Best balanced accuracy:",
        f"{best_score * 100:.2f}%"
    )

    # ======================================
    # SAVE EXPERIMENTAL MODEL
    # ======================================

    MODEL_DIR.mkdir(exist_ok=True)

    joblib.dump(
        best_model,
        CANDIDATE_MODEL_PATH
    )

    print("\nExperimental model saved:")
    print(CANDIDATE_MODEL_PATH)

    print("\nExisting production model preserved:")
    print(CURRENT_MODEL_PATH)

    print("\nPrevious candidate model preserved:")
    print(PREVIOUS_CANDIDATE_PATH)

    # ======================================
    # SAVE EVALUATION REPORT
    # ======================================

    with REPORT_PATH.open("w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Model",
                "Accuracy",
                "Balanced Accuracy",
                "Macro Precision",
                "Macro Recall",
                "Macro F1",
            ],
        )

        writer.writeheader()
        writer.writerows(evaluation_rows)

    print("\nEvaluation report saved:")
    print(REPORT_PATH.resolve())

    print("\n" + "=" * 60)
    print("30 FEATURE EXPERIMENT COMPLETED")
    print("=" * 60)


# ==========================================
# RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    main()
