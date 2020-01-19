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


def test_args_chaining():
    cmd = Cmd("cp")
    assert cmd.args == ["cp"]

    cmd = cmd("src.txt", "dst.txt")
    assert cmd.args == ["cp", "src.txt", "dst.txt"]

    cmd = Cmd("ls")("--all")("dir1", "dir2")
    assert cmd.args == ["ls", "--all", "dir1", "dir2"]


def test_args_chaining_does_not_mutate():
    cp = Cmd("cp")
    cp_verbose = cp("--verbose")  # This should not mutate `cp`.
    assert cp.args == ["cp"]
    assert cp_verbose.args == ["cp", "--verbose"]


def test_cmd_args():
    ls = Cmd("ls", "--recursive", "--size")
    assert ls.args == ["ls", "--recursive", "--size"]
