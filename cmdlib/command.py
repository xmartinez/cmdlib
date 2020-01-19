from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List, Optional


def Cmd(program):
    return Command(args=[program])


@dataclass
class Command:
    args: List[str]

    def run(self) -> ExitStatus:
        p = subprocess.run(self.args)
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
