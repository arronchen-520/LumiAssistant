"""
voice.py - Record audio + transcribe via Groq Whisper using OpenAI SDK.

Groq exposes an OpenAI-compatible /audio/transcriptions endpoint,
so we use the official openai package — no groq package needed.
"""
import io
import os
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

SAMPLE_RATE = 16000
CHANNELS    = 1
GROQ_BASE   = "https://api.groq.com/openai/v1"
WHISPER_MODEL = "whisper-large-v3-turbo"


class VoiceRecorder:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key.startswith("your_"):
            raise ValueError("Please set GROQ_API_KEY in your .env file. Get a free key at https://console.groq.com")
        self._client    = OpenAI(api_key=api_key, base_url=GROQ_BASE)
        self._recording = False
        self._frames: list = []
        self._thread: threading.Thread | None = None

    def start(self):
        """Begin recording from the default microphone."""
        self._frames    = []
        self._recording = True
        self._thread    = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self) -> bytes:
        """Stop recording and return raw WAV bytes. Returns b'' if nothing recorded."""
        self._recording = False
        if self._thread:
            self._thread.join(timeout=3)
        if not self._frames:
            return b""
        audio = np.concatenate(self._frames, axis=0)
        buf   = io.BytesIO()
        sf.write(buf, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        buf.seek(0)
        return buf.read()

    def _record_loop(self):
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16") as stream:
            while self._recording:
                data, _ = stream.read(1024)
                self._frames.append(data.copy())

    def transcribe(self, wav_bytes: bytes, language: str = "zh") -> str:
        """
        Transcribe WAV bytes using Groq Whisper via OpenAI-compatible API.
        language: ISO 639-1 code ("zh", "en", "ja" …) or None for auto-detect.
        """
        if not wav_bytes:
            return ""
        buf      = io.BytesIO(wav_bytes)
        buf.name = "audio.wav"

        kwargs: dict = dict(file=buf, model=WHISPER_MODEL, response_format="text")
        if language:
            kwargs["language"] = language

        response = self._client.audio.transcriptions.create(**kwargs)
        return (response if isinstance(response, str) else response.text).strip()
