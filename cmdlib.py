from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Union

__version__ = "0.3.0"


class CommandError(Exception):
    pass


def Cmd(program, *args: str, **kw: str) -> Command:
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

    def json(self, check=True) -> Any:
        p = subprocess.run(self.args, capture_output=True)
        if check and p.returncode != 0:
            raise CommandError()
        return json.loads(p.stdout)

    def out(self, check=True) -> str:
        p = subprocess.run(self.args, capture_output=True)
        if check and p.returncode != 0:
            raise CommandError()
        return p.stdout.decode()

    def run(self, check=True) -> ExitStatus:
        p = subprocess.run(self.args)
        if check and p.returncode != 0:
            raise CommandError()
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
