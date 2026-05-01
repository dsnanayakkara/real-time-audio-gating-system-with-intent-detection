from __future__ import annotations


class KeywordSpotter:
    def __init__(self, model_path: str, sample_rate: int):
        import json
        from vosk import KaldiRecognizer, Model

        model = Model(model_path)
        grammar = json.dumps(["comms on", "comms off", "[unk]"])
        self.recognizer = KaldiRecognizer(model, sample_rate, grammar)

    def accept_frame(self, frame: bytes) -> str | None:
        import json

        if self.recognizer.AcceptWaveform(frame):
            text = json.loads(self.recognizer.Result()).get("text", "")
        else:
            text = json.loads(self.recognizer.PartialResult()).get("partial", "")

        if text == "comms on":
            return "start"
        if text == "comms off":
            return "stop"
        return None


def validate_model_path(model_path: str) -> None:
    from pathlib import Path

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Vosk model path not found: {model_path}. "
            "Download a small English model and pass --vosk-model."
        )
