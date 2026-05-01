# real-time-audio-gating-system-with-intent-detection

Minimal local MVP for real-time voice-controlled microphone gating.

## What it does
- Mic input is captured at **16kHz mono** in **10/20/30ms frames**.
- Gate starts in **CLOSED** state (muted).
- Saying **"comms on"** opens the gate.
- While **OPEN**, frames are forwarded.
- Gate closes when:
  - silence exceeds threshold (default **1200ms**), or
  - **"comms off"** is detected.
- Includes a pre-roll buffer (default **300ms**) to reduce clipped first syllables.

## Files
- `audio_input.py` - mic capture and rolling pre-roll buffer
- `vad.py` - WebRTC VAD wrapper
- `keyword.py` - offline keyword spotting via Vosk grammar
- `state_machine.py` - CLOSED/OPEN gate logic
- `main.py` - real-time loop and gate behavior

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download a small Vosk English model (for example `vosk-model-small-en-us-0.15`) and unpack it locally.

## Run
```bash
python main.py --vosk-model /path/to/vosk-model-small-en-us-0.15 --simulate-output
```

Useful options:
```bash
python main.py \
  --vosk-model /path/to/model \
  --frame-ms 20 \
  --vad-level 2 \
  --silence-ms 1200 \
  --preroll-ms 300 \
  --simulate-output
```

## Notes
- `--simulate-output` prints forwarding events instead of routing to a virtual microphone.
- Replace `forward_audio()` in `main.py` to integrate with your local virtual mic stack.
- For low latency, keep frame size at 20ms and avoid heavy work inside the audio callback.
