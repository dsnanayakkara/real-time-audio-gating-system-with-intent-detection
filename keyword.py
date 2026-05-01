from __future__ import annotations

_PY_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await", "break",
    "class", "continue", "def", "del", "elif", "else", "except", "finally", "for",
    "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or",
    "pass", "raise", "return", "try", "while", "with", "yield",
}


def iskeyword(value: str) -> bool:
    return value in _PY_KEYWORDS


class KeywordSpotter:
    def __init__(self, model_path: str, sample_rate: int):
        import json
        from vosk import KaldiRecognizer, Model

        model = Model(model_path)
        grammar = json.dumps(["comms on", "comms off", "[unk]"])
        self.recognizer = KaldiRecognizer(model, sample_rate, grammar)

    def accept_frame(self, frame: bytes) -> str | None:
        import json

        self.recognizer.AcceptWaveform(frame)
        partial = json.loads(self.recognizer.PartialResult()).get("partial", "")
        if partial == "comms on":
            return "start"
        if partial == "comms off":
            return "stop"

        final_text = json.loads(self.recognizer.Result()).get("text", "")
        if final_text == "comms on":
            return "start"
        if final_text == "comms off":
            return "stop"
        return None


def validate_model_path(model_path: str) -> None:
    from pathlib import Path

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Vosk model path not found: {model_path}. "
            "Download a small English model and pass --vosk-model."
        )
