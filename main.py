from __future__ import annotations

import argparse
import queue
import time

from audio_input import AudioConfig, MicStream
from keyword import KeywordSpotter, validate_model_path
from state_machine import GateConfig, GateState, GateStateMachine
from vad import VAD


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time voice-controlled microphone gate"
    )
    parser.add_argument("--vosk-model", required=True, help="Path to Vosk model")
    parser.add_argument("--frame-ms", type=int, default=20, choices=[10, 20, 30])
    parser.add_argument("--vad-level", type=int, default=2, choices=[0, 1, 2, 3])
    parser.add_argument("--silence-ms", type=int, default=1200)
    parser.add_argument("--preroll-ms", type=int, default=300)
    parser.add_argument(
        "--simulate-output",
        action="store_true",
        help="Print forwarding events instead of writing to virtual mic",
    )
    return parser.parse_args()


def forward_audio(frame: bytes, simulate_output: bool) -> None:
    if simulate_output:
        print(f"[gate] forwarded {len(frame)} bytes")
    else:
        # Placeholder for virtual microphone output integration.
        # Example options: sounddevice.OutputStream or PulseAudio null sink/loopback.
        pass


def main() -> None:
    args = parse_args()
    validate_model_path(args.vosk_model)

    cfg = AudioConfig(frame_ms=args.frame_ms, preroll_ms=args.preroll_ms)
    mic = MicStream(cfg)
    vad = VAD(args.vad_level)
    kws = KeywordSpotter(args.vosk_model, cfg.sample_rate)
    sm = GateStateMachine(GateConfig(silence_timeout_ms=args.silence_ms))

    mic.start()
    print("[main] running. Say 'comms on' to open, 'comms off' to close.")

    try:
        while True:
            try:
                frame = mic.read()
            except queue.Empty:
                continue
            now_ms = int(time.monotonic() * 1000)
            speech = vad.is_speech(frame, cfg.sample_rate)
            if speech:
                print("[vad] speech")

            keyword = kws.accept_frame(frame) if speech else None
            if keyword:
                print(f"[kws] {keyword}")

            prev_state = sm.state
            state = sm.handle(now_ms=now_ms, speech=speech, keyword=keyword)

            if prev_state == GateState.CLOSED and state == GateState.OPEN:
                for pre in mic.get_preroll():
                    forward_audio(pre, args.simulate_output)
            elif state == GateState.OPEN:
                forward_audio(frame, args.simulate_output)

    except KeyboardInterrupt:
        print("\n[main] stopping")
    finally:
        mic.close()


if __name__ == "__main__":
    main()
