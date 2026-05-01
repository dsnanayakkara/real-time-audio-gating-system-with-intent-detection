from state_machine import GateConfig, GateState, GateStateMachine


def test_closed_opens_on_start_keyword():
    sm = GateStateMachine(GateConfig(silence_timeout_ms=1200))
    state = sm.handle(now_ms=1000, speech=True, keyword="start")
    assert state == GateState.OPEN


def test_open_closes_on_stop_keyword():
    sm = GateStateMachine(GateConfig(silence_timeout_ms=1200))
    sm.handle(now_ms=1000, speech=True, keyword="start")
    state = sm.handle(now_ms=1100, speech=True, keyword="stop")
    assert state == GateState.CLOSED


def test_open_closes_on_silence_timeout():
    sm = GateStateMachine(GateConfig(silence_timeout_ms=500))
    sm.handle(now_ms=1000, speech=True, keyword="start")
    state = sm.handle(now_ms=1601, speech=False, keyword=None)
    assert state == GateState.CLOSED


def test_speech_updates_last_speech_timestamp():
    sm = GateStateMachine(GateConfig(silence_timeout_ms=1200))
    sm.handle(now_ms=2000, speech=True, keyword=None)
    assert sm.last_speech_ms == 2000
