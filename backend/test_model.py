
import joblib
from pathlib import Path
from audio_features import extract_features

# ==========================================
# 1. LOAD BOTH TRAINED MODELS
# ==========================================

logistic_model = joblib.load("models/voice_detector.joblib")
svm_model = joblib.load("models/voice_detector_candidate.joblib")

# ==========================================
# 2. SELECT THREE TEST RECORDINGS
# ==========================================

files = [
    {
        "name": "Your genuine recording",
        "path": Path(
            r"C:\Users\7905n\Downloads\record_out.wav"
        )
    },
    {
        "name": "ASVspoof genuine recording",
        "path": Path(
            r"C:\Users\7905n\Downloads\LA\LA\ASVspoof2019_LA_dev\flac\LA_D_1047731.flac"
        )
    },
    {
        "name": "ASVspoof spoof recording",
        "path": Path(
            r"C:\Users\7905n\Downloads\LA\LA\ASVspoof2019_LA_dev\flac\LA_D_1008730.flac"
        )
    }
]

# ==========================================
# 3. MODELS TO COMPARE
# ==========================================

models = [
    ("Logistic Regression", logistic_model),
    ("SVM (RBF)", svm_model)
]

# ==========================================
# 4. TEST AND COMPARE
# ==========================================

for item in files:

    file = item["path"]

    print("\n" + "=" * 60)
    print("TESTING:", item["name"])
    print("Filename:", file.name)
    print("=" * 60)

    if not file.exists():
        print("ERROR: Audio file not found!")
        continue

    try:
        # Extract the same 26 MFCC features for both models
        features = extract_features(str(file)).reshape(1, -1)

        print("Feature shape:", features.shape)

        for model_name, model in models:

            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]

            classification = (
                "SPOOF" if prediction == 1 else "BONAFIDE"
            )

            bonafide_score = probabilities[0] * 100
            spoof_score = probabilities[1] * 100

            print("\nModel:", model_name)
            print("Prediction:", classification)
            print(f"Bonafide score: {bonafide_score:.2f}%")
            print(f"Spoof score: {spoof_score:.2f}%")

    except Exception as error:
        print("ERROR:", error)

print("\n" + "=" * 60)
print("MODEL COMPARISON COMPLETED")
print("=" * 60)
