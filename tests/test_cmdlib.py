"""cmdlib test suite."""

import pytest

from cmdlib import __version__, Cmd, CommandError


def test_version():
    assert __version__ == "0.2.0"


def test_run_status():
    status = Cmd("true").run()
    assert status.success()
    assert status.code == 0

    status = Cmd("false").run(check=False)
    assert not status.success()
    assert status.code == 1


def test_run_raises():
    with pytest.raises(CommandError):
        Cmd("false").run()


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


def test_kwargs_options():
    cmd = Cmd("cp")(target_directory="..")
    assert cmd.args == ["cp", "--target-directory=.."]


def test_kwargs_bool_to_option_flag():
    cmd = Cmd("cp")(verbose=True)
    assert cmd.args == ["cp", "--verbose"]


def test_cmd_args():
    ls = Cmd("ls", "--recursive", "--size")
    assert ls.args == ["ls", "--recursive", "--size"]


def test_cmd_kwargs():
    ls = Cmd("ls", "dir1", color="never")
    assert ls.args == ["ls", "dir1", "--color=never"]


def test_out():
    out = Cmd("echo", "some output").out()
    assert out == "some output\n"
