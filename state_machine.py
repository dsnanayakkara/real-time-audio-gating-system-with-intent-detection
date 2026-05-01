from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GateState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"


@dataclass
class GateConfig:
    silence_timeout_ms: int = 1200


class GateStateMachine:
    def __init__(self, config: GateConfig):
        self.config = config
        self.state = GateState.CLOSED
        self.last_speech_ms = 0

    def handle(self, *, now_ms: int, speech: bool, keyword: str | None) -> GateState:
        if speech:
            self.last_speech_ms = now_ms

        if self.state == GateState.CLOSED:
            if keyword == "start":
                self.state = GateState.OPEN
                print(f"[state] {self.state} (keyword=start)")
        else:  # OPEN
            if keyword == "stop":
                self.state = GateState.CLOSED
                print(f"[state] {self.state} (keyword=stop)")
            elif now_ms - self.last_speech_ms > self.config.silence_timeout_ms:
                self.state = GateState.CLOSED
                print(
                    f"[state] {self.state} "
                    f"(silence>{self.config.silence_timeout_ms}ms)"
                )
        return self.state
