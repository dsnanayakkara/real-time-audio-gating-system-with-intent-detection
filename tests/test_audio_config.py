from audio_input import AudioConfig


def test_audio_config_derived_sizes():
    cfg = AudioConfig(sample_rate=16000, frame_ms=20, preroll_ms=300)
    assert cfg.frame_samples == 320
    assert cfg.frame_bytes == 640
    assert cfg.preroll_frames == 15
