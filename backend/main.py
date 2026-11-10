
from io import BytesIO
from pathlib import Path
from audio_features import extract_features

import joblib
import librosa
import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VoiceShield API",
    description="Audio analysis backend for the VoiceShield capstone.",
    version="0.2.0",
)

MODEL_PATH = Path("models/voice_detector.joblib")

model = joblib.load(MODEL_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".wav", ".flac", ".ogg"}
MAX_FILE_SIZE = 20 * 1024 * 1024


@app.get("/")
def home():
    return {
        "project": "VoiceShield",
        "status": "online",
        "detection_model": "logistic_regression_mfcc_v1",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # 1. Validate file extension
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="For now, upload a WAV, FLAC, or OGG file.",
        )

    # 2. Read the uploaded file with a size limit
    audio_bytes = await file.read(MAX_FILE_SIZE + 1)

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="The file is empty.",
        )

    if len(audio_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 20 MB.",
        )

    # 3. Decode the audio
    try:
        audio, sample_rate = sf.read(
            BytesIO(audio_bytes),
            dtype="float32",
            always_2d=True,
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not decode this audio file. "
                "Please try a valid WAV, FLAC, or OGG recording."
            ),
        )

    # 4. Validate decoded audio
    if audio.shape[0] == 0 or sample_rate <= 0:
        raise HTTPException(
            status_code=400,
            detail="The audio contains no samples.",
        )

    if not np.isfinite(audio).all():
        raise HTTPException(
            status_code=400,
            detail="The audio contains invalid numeric samples.",
        )

    # 5. Calculate basic audio properties
    duration = audio.shape[0] / sample_rate
    channels = audio.shape[1]

    peak_amplitude = float(np.max(np.abs(audio)))
    rms_amplitude = float(np.sqrt(np.mean(audio ** 2)))

    
    # 6. Extract the shared 26-feature representation
    try:
        feature_vector = extract_features(audio_bytes)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Audio feature extraction failed: {str(exc)}",
        )


    # 7. Predict whether the audio is genuine or spoofed
    try:
        prediction = int(model.predict([feature_vector])[0])
        probabilities = model.predict_proba([feature_vector])[0]

        spoof_probability = float(probabilities[1])

        classification = "spoof" if prediction == 1 else "bonafide"

        risk_score = round(spoof_probability * 100, 2)

        confidence = round(float(max(probabilities)) * 100, 2)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {str(exc)}",
        )

    # 8. Return audio metadata, features, and prediction
    return {
        "filename": Path(file.filename or "audio").name,
        "file_size_bytes": len(audio_bytes),
        "duration_seconds": round(duration, 2),
        "sample_rate": sample_rate,
        "channels": channels,
        "peak_amplitude": round(peak_amplitude, 4),
        "rms_amplitude": round(rms_amplitude, 4),
        "features": {
            "mfcc_coefficients": 13,
            "feature_count": len(feature_vector),
            "mfcc_mean": [
                round(float(value), 4)
                for value in feature_vector[:13]
            ],
            "mfcc_std": [
                round(float(value), 4)
                for value in feature_vector[13:]
            ],
        },
        "classification": classification,
        "risk_score": risk_score,
        "confidence": confidence,
        "detection_model": "logistic_regression_mfcc_v1",
        "message": "Audio classification completed successfully.",
    }
