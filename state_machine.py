from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

_log = logging.getLogger(__name__)


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
                self.last_speech_ms = now_ms
                self.state = GateState.OPEN
                _log.info("gate OPEN (keyword=start)")
        else:  # OPEN
            if keyword == "stop":
                self.state = GateState.CLOSED
                _log.info("gate CLOSED (keyword=stop)")
            elif now_ms - self.last_speech_ms > self.config.silence_timeout_ms:
                self.state = GateState.CLOSED
                _log.info("gate CLOSED (silence>%dms)", self.config.silence_timeout_ms)
        return self.state
