
from pathlib import Path
import numpy as np
import joblib

from audio_features import extract_features

DATASET_ROOT = Path(r"C:\Users\7905n\Downloads\LA\LA")

PROTOCOL = (
    DATASET_ROOT
    / "ASVspoof2019_LA_cm_protocols"
    / "ASVspoof2019.LA.cm.dev.trl.txt"
)

AUDIO_DIR = DATASET_ROOT / "ASVspoof2019_LA_dev" / "flac"

MODEL_PATH = Path("models/voice_detector_candidate.joblib")

RECORDING = Path(r"C:\Users\7905n\Downloads\record_out.wav")

SAMPLES_PER_CLASS = 100


def main():
    model = joblib.load(MODEL_PATH)
    scaler = model.named_steps["standardscaler"]

    user_features = extract_features(str(RECORDING))
    user_z = scaler.transform([user_features])[0]

    groups = {"bonafide": [], "spoof": []}

    rows = PROTOCOL.read_text().splitlines()

    for row in rows:
        fields = row.split()
        audio_id = fields[1]
        label = fields[-1]

        if label in groups and len(groups[label]) < SAMPLES_PER_CLASS:
            audio_path = AUDIO_DIR / f"{audio_id}.flac"
            features = extract_features(str(audio_path))
            groups[label].append(features)

        if all(len(v) >= SAMPLES_PER_CLASS for v in groups.values()):
            break

    for label in groups:
        groups[label] = np.asarray(groups[label])
        print(f"{label}: {len(groups[label])} recordings")

    print("\nFEATURE COMPARISON")
    print("-" * 75)

    for i in range(26):
        genuine = scaler.transform(groups["bonafide"])[:, i]
        spoof = scaler.transform(groups["spoof"])[:, i]

        print(
            f"Feature {i+1:02} | "
            f"Your voice: {user_z[i]:7.2f} | "
            f"Genuine avg: {np.mean(genuine):7.2f} | "
            f"Spoof avg: {np.mean(spoof):7.2f}"
        )


if __name__ == "__main__":
    main()
