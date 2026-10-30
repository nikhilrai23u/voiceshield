
import librosa
import numpy as np
from io import BytesIO


def extract_features(audio_source):
    if isinstance(audio_source, (bytes, bytearray)):
        audio, sample_rate = librosa.load(
            BytesIO(audio_source),
            sr=16000,
            mono=True,
        )
    else:
        audio, sample_rate = librosa.load(
            audio_source,
            sr=16000,
            mono=True,
        )

    if len(audio) == 0:
        raise ValueError("Audio file is empty.")

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sample_rate,
        n_mfcc=13,
    )

    mfcc_means = np.mean(mfcc, axis=1)
    mfcc_stds = np.std(mfcc, axis=1)

    return np.concatenate([mfcc_means, mfcc_stds])
