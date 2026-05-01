from __future__ import annotations

import queue
from collections import deque
from dataclasses import dataclass



@dataclass
class AudioConfig:
    sample_rate: int = 16_000
    channels: int = 1
    frame_ms: int = 20
    preroll_ms: int = 300

    @property
    def frame_samples(self) -> int:
        return int(self.sample_rate * self.frame_ms / 1000)

    @property
    def frame_bytes(self) -> int:
        return self.frame_samples * 2  # int16 mono

    @property
    def preroll_frames(self) -> int:
        return max(1, self.preroll_ms // self.frame_ms)


class MicStream:
    """Callback-based microphone stream producing 16-bit mono PCM frames."""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.frames: queue.Queue[bytes] = queue.Queue(maxsize=256)
        self.preroll = deque(maxlen=self.config.preroll_frames)
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            # Keep lightweight logging in callback.
            print(f"[audio] callback status={status}")
        if frames != self.config.frame_samples:
            return

        frame = bytes(indata)
        self.preroll.append(frame)
        try:
            self.frames.put_nowait(frame)
        except queue.Full:
            # Drop oldest item then push newest to keep latency bounded.
            try:
                _ = self.frames.get_nowait()
            except queue.Empty:
                pass
            self.frames.put_nowait(frame)

    def start(self) -> None:
        import sounddevice as sd

        self._stream = sd.RawInputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="int16",
            blocksize=self.config.frame_samples,
            callback=self._callback,
        )
        self._stream.start()

    def read(self, timeout: float = 0.5) -> bytes:
        return self.frames.get(timeout=timeout)

    def get_preroll(self) -> list[bytes]:
        return list(self.preroll)

    def close(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
