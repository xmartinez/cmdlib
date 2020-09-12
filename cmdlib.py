from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
from dataclasses import dataclass
from textwrap import indent
from typing import TYPE_CHECKING, Any, List, NoReturn, Optional, Union

__version__ = "0.5.1"


if TYPE_CHECKING:
    StrPath = Union[str, os.PathLike[str]]
else:
    StrPath = Union[str, os.PathLike]


def _restore_signals() -> None:
    sig_restore = {"SIGPIPE", "SIGXFZ", "SIGXFSZ"}
    sigset = {
        signal.Signals[name]
        for name in sig_restore
        if name in signal.Signals.__members__
    }
    for signum in sigset:
        signal.signal(signum, signal.SIG_DFL)


class CommandError(Exception):
    def __init__(
        self,
        command: Command,
        status: ExitStatus,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ):
        self.command = str(command)
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    def _format_output(self, prefix: str, output: Optional[str]) -> str:
        if not output:
            return ""
        formatted = indent(output.rstrip("\n"), "  ")
        return f"\n{prefix}\n\n{formatted}\n"

    def _format_command(self) -> str:
        cmd = str(self.command)
        if len(cmd) < 22 and "\n" not in cmd:
            return f" {cmd}"
        formatted = indent(cmd.rstrip("\n"), "  ")
        return f"\n\n{formatted}\n"

    def __str__(self) -> str:
        return (
            f"command exited with non-zero status code {self.status.code}:"
            f"{self._format_command()}"
            f"{self._format_output('Stdout:', self.stdout)}"
            f"{self._format_output('Stderr:', self.stderr)}"
        )


def Cmd(program: StrPath, *args: StrPath, **kw: str) -> Command:
    return Command(args=[program])(*args, **kw)


def _item_as_option(k: str, v: Union[bool, str]) -> str:
    k = k.replace("_", "-")
    return f"--{k}" if v is True else f"--{k}={v}"


@dataclass
class Command:
    args: List[StrPath]

    def __call__(self, *args: StrPath, **kw: Union[bool, str]) -> Command:
        new_args = self.args[:]
        new_args.extend(args)
        new_args.extend(_item_as_option(k, v) for k, v in kw.items())
        return Command(args=new_args)

    def __str__(self) -> str:
        return " ".join(map(shlex.quote, [os.fspath(arg) for arg in self.args]))

    def exec(self) -> NoReturn:
        # Restore signals that the Python interpreter has called SIG_IGN on to SIG_DFL.
        #
        # Note that `subprocess.run()` already does this internally
        # (`restore_signals=True`), so all spawn-like methods (`json()`, `out()`,
        # `run()`) also reset signals before `exec`.
        #
        _restore_signals()

        os.execvp(self.args[0], [os.fspath(arg) for arg in self.args])

    def json(self) -> Any:
        return json.loads(self.out())

    def out(self) -> str:
        p = subprocess.run(self.args, capture_output=True)
        status = ExitStatus(status=p.returncode)
        if not status.success():
            raise CommandError(
                command=self,
                status=status,
                stdout=p.stdout.decode(),
                stderr=p.stderr.decode(),
            )
        return p.stdout.decode()

    def run(self) -> ExitStatus:
        p = subprocess.run(self.args)
        status = ExitStatus(status=p.returncode)
        if not status.success():
            raise CommandError(command=self, status=status)
        return ExitStatus(p.returncode)


@dataclass
class ExitStatus:
    status: int

    def success(self) -> bool:
        return self.status == 0

    @property
    def code(self) -> Optional[int]:
        # TODO: Handle signals.
        return self.status
