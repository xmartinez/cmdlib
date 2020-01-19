from cmdlib import __version__, Cmd


def test_version():
    assert __version__ == "0.1.0"


def test_run_status():
    status = Cmd("true").run()
    assert status.success()
    assert status.code == 0

    status = Cmd("false").run()
    assert not status.success()
    assert status.code == 1
