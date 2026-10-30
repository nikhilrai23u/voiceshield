
from io import BytesIO
from pathlib import Path
from audio_features import extract_features


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
        "detection_model": "not_integrated",
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

    # 6. Convert to mono for feature extraction
    mono_audio = audio.mean(axis=1)

    # 7. Extract 13 MFCC coefficients using Librosa
    try:
        mfcc = librosa.feature.mfcc(
            y=mono_audio,
            sr=sample_rate,
            n_mfcc=13,
        )

        # Average each coefficient across audio frames
        mfcc_mean = mfcc.mean(axis=1)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Audio feature extraction failed: {str(exc)}",
        )

    # 8. Return audio metadata and extracted features
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
            "mfcc_mean": [
                round(float(value), 4)
                for value in mfcc_mean
            ],
        },
        "classification": None,
        "risk_score": None,
        "confidence": None,
        "detection_model": "not_integrated",
        "message": (
            "Audio decoded and MFCC features extracted successfully. "
            "Voice-cloning classification is not available yet."
        ),
    }
