from __future__ import annotations

import webrtcvad


class VAD:
    def __init__(self, aggressiveness: int = 2):
        if aggressiveness not in (0, 1, 2, 3):
            raise ValueError("aggressiveness must be 0..3")
        self._vad = webrtcvad.Vad(aggressiveness)

    def is_speech(self, frame: bytes, sample_rate: int) -> bool:
        return self._vad.is_speech(frame, sample_rate)
