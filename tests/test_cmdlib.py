"""cmdlib test suite."""

import os
import traceback
from pathlib import Path
from textwrap import dedent

import pytest

from cmdlib import __version__, Cmd, CommandError, ExitStatus


def test_version() -> None:
    assert __version__ == "0.8.0"


def test_current_dir(tmp_path: Path) -> None:
    cwd = Cmd("pwd").current_dir(tmp_path).output().rstrip()
    assert Path(cwd) == tmp_path

    # Add an argument after `current_dir()` to ensure that it is preserved.
    cwd = Cmd("pwd").current_dir(tmp_path)("-P").output().rstrip()
    assert Path(cwd) == tmp_path

    # `None` should preserve current working directory.
    cwd = Cmd("pwd").current_dir(None).output().rstrip()
    assert cwd == os.getcwd()


def test_env() -> None:
    script = "\n".join(["import json, os", "print(json.dumps(dict(os.environ)))"])
    cmd = Cmd("python")("-c", script)

    # Modify child environment.
    env = cmd.env(VAR1="VALUE_1", VAR2="VALUE_2").json()
    assert env["VAR1"] == "VALUE_1"
    assert env["VAR2"] == "VALUE_2"

    # Current process should not be modified.
    assert "VAR1" not in os.environ
    assert "VAR2" not in os.environ

    # Chaining.
    env = cmd.env(VAR1="VALUE_1").env(VAR2="VALUE_2").json()
    assert env["VAR1"] == "VALUE_1"
    assert env["VAR2"] == "VALUE_2"


def test_env_args() -> None:
    script = "\n".join(["import json, os", "print(json.dumps(dict(os.environ)))"])
    cmd = Cmd("python")

    # Modify environment.
    cmd = cmd.env(VAR1="VALUE_1")

    # Add args.
    cmd_args = cmd("-c", script)
    env = cmd_args.json()
    assert env["VAR1"] == "VALUE_1"


def test_env_cwd() -> None:
    script = "\n".join(["import json, os", "print(json.dumps(dict(os.environ)))"])
    cmd = Cmd("python")("-c", script)

    # Modify environment.
    cmd = cmd.env(VAR1="VALUE_1")

    # Set cwd.
    cmd_cwd = cmd.current_dir(Path("/"))
    env = cmd_cwd.json()
    assert env["VAR1"] == "VALUE_1"


def test_env_does_not_mutate() -> None:
    script = "\n".join(["import json, os", "print(json.dumps(dict(os.environ)))"])
    cmd = Cmd("python")("-c", script)
    cmd_env = cmd.env(VAR1="VALUE1")

    # The env variable should only apply to the second command.
    assert "VAR1" not in cmd.json()
    assert "VAR1" in cmd_env.json()


def test_env_exec() -> None:
    script = [
        "import os",
        "assert os.environ['VAR1'] == 'VALUE_1'",
    ]
    check_cmd = Cmd("python")("-c", "\n".join(script))

    # Modify child environment.
    check_cmd = check_cmd.env(VAR1="VALUE_1")

    # Exec child.
    pid = os.fork()
    if not pid:
        # Child process.
        check_cmd.exec()
        os._exit(1)
    else:
        # Parent (current) process.
        _, status = os.waitpid(pid, 0)

    # Child status ok.
    assert os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0

    # Current process should not be modified.
    assert "VAR1" not in os.environ


def test_exec() -> None:
    script = "\n".join(["import cmdlib", "cmdlib.Cmd('echo', 'arg1', 'arg2').exec()"])
    output = Cmd("python3")("-c", script).out()
    assert output == "arg1 arg2\n"


def test_run() -> None:
    Cmd("true").run()


def test_run_raises() -> None:
    with pytest.raises(CommandError):
        Cmd("false").run()


def test_run_path_like() -> None:
    Cmd("echo")(Path(".")).run()


def test_status() -> None:
    status = Cmd("true").status()
    assert status.success()
    assert status.code == 0

    status = Cmd("false").status()
    assert not status.success()
    assert status.code == 1


def test_command_error_captures_output() -> None:
    script = "\n".join(
        [
            "import sys",
            "print('stdout message')",
            "print('stderr message', file=sys.stderr)",
            "sys.exit(42)",
        ]
    )
    with pytest.raises(CommandError) as err:
        Cmd("python3")("-c", script).out()

    traceback.print_exception(err.type, err.value, err.tb)
    exc = err.value
    assert exc.status.code == 42
    assert exc.command.startswith("python3 -c '")
    assert exc.stdout == "stdout message\n"
    assert exc.stderr == "stderr message\n"


def test_command_error_format() -> None:
    cmd = Cmd("echo")("some arg")
    exc = CommandError(command=cmd, status=ExitStatus(status=42))
    message = list(traceback.format_exception_only(type(exc), exc))
    assert message == [
        "cmdlib.CommandError: command exited with non-zero status code 42: "
        "echo 'some arg'\n"
    ]


def test_command_error_format_long() -> None:
    cmd = Cmd("grep")(fixed_strings=True, recursive=True)("needle", ".")
    exc = CommandError(
        command=cmd,
        status=ExitStatus(status=2),
        stdout="Stdout message.\nMore stdout.\n",
        stderr="Stderr message.\nMore stderr.\n",
    )
    message = list(traceback.format_exception_only(type(exc), exc))
    print("".join(message))
    assert message[0].strip() == (
        dedent(
            """
            cmdlib.CommandError: command exited with non-zero status code 2:

              grep --fixed-strings --recursive needle .

            Stdout:

              Stdout message.
              More stdout.

            Stderr:

              Stderr message.
              More stderr.
            """
        ).strip()
    )


def test_command_str_quoted() -> None:
    cmd = Cmd("echo")("some arg")
    assert str(cmd) == r"echo 'some arg'"


def test_command_str_path_like() -> None:
    cmd = Cmd("ls")(Path("."))
    assert str(cmd) == "ls ."


def test_args_chaining() -> None:
    cmd = Cmd("cp")
    assert cmd.args == ["cp"]

    cmd = cmd("src.txt", "dst.txt")
    assert cmd.args == ["cp", "src.txt", "dst.txt"]

    cmd = Cmd("ls")("--all")("dir1", "dir2")
    assert cmd.args == ["ls", "--all", "dir1", "dir2"]


def test_args_chaining_does_not_mutate() -> None:
    cp = Cmd("cp")
    cp_verbose = cp("--verbose")  # This should not mutate `cp`.
    assert cp.args == ["cp"]
    assert cp_verbose.args == ["cp", "--verbose"]


def test_kwargs_options() -> None:
    cmd = Cmd("cp")(target_directory="..")
    assert cmd.args == ["cp", "--target-directory=.."]


def test_kwargs_bool_to_option_flag() -> None:
    cmd = Cmd("cp")(verbose=True)
    assert cmd.args == ["cp", "--verbose"]


def test_cmd_args() -> None:
    ls = Cmd("ls", "--recursive", "--size")
    assert ls.args == ["ls", "--recursive", "--size"]


def test_cmd_kwargs() -> None:
    ls = Cmd("ls", "dir1", color="never")
    assert ls.args == ["ls", "dir1", "--color=never"]


def test_json() -> None:
    out = Cmd("echo", '{"a":1,"b":2,"c":null}').json()
    assert out == dict(a=1, b=2, c=None)


def test_json_raises() -> None:
    with pytest.raises(CommandError):
        Cmd("false").json()


def test_out() -> None:
    out = Cmd("echo", "some output").output()
    assert out == "some output\n"


def test_output() -> None:
    out = Cmd("echo", "some output").output()
    assert out == "some output\n"


def test_output_bytes() -> None:
    out = Cmd("echo", "12345").output_bytes()
    assert out == b"12345\n"
