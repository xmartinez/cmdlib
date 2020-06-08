from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from textwrap import indent
from typing import Any, List, Optional, Union

__version__ = "0.4.0"


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


def Cmd(program: str, *args: str, **kw: str) -> Command:
    return Command(args=[program])(*args, **kw)


def _item_as_option(k: str, v: Union[bool, str]) -> str:
    k = k.replace("_", "-")
    return f"--{k}" if v is True else f"--{k}={v}"


@dataclass
class Command:
    args: List[str]

    def __call__(self, *args: str, **kw: Union[bool, str]) -> Command:
        new_args = self.args[:]
        new_args.extend(args)
        new_args.extend(_item_as_option(k, v) for k, v in kw.items())
        return Command(args=new_args)

    def __str__(self) -> str:
        return " ".join(map(shlex.quote, self.args))

    def json(self, check: bool = True) -> Any:
        return json.loads(self.out())

    def out(self, check: bool = True) -> str:
        p = subprocess.run(self.args, capture_output=True)
        status = ExitStatus(status=p.returncode)
        if check and not status.success():
            raise CommandError(
                command=self,
                status=status,
                stdout=p.stdout.decode(),
                stderr=p.stderr.decode(),
            )
        return p.stdout.decode()

    def run(self, check: bool = True) -> ExitStatus:
        p = subprocess.run(self.args)
        status = ExitStatus(status=p.returncode)
        if check and not status.success():
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
