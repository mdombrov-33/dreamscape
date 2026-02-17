import numpy as np
from loguru import logger

_whisper = None


def _get_whisper():
    global _whisper
    if _whisper is None:
        from transformers import pipeline

        logger.info("Loading Whisper model...")
        _whisper = pipeline(
            "automatic-speech-recognition", model="openai/whisper-small", device="cpu"
        )  # noqa: E501
        logger.info("Whisper loaded.")
    return _whisper


def transcribe_audio(audio):
    if audio is None:
        return ""
    sample_rate, data = audio
    if data.ndim > 1:
        data = data.mean(axis=1)
    audio_float = data.astype(np.float32) / 32768.0
    result: dict = _get_whisper()({"sampling_rate": sample_rate, "raw": audio_float})  # type: ignore[assignment]
    return result["text"].strip()
