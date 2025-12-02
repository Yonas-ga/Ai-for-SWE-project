from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from release import Release
from programmer import Programmer


@dataclass
class ReleasePlan:
    """
    Master plan containing all releases and assigned programmers.

    Attributes:
        releases: List of releases included in the plan.
        programmers: List of programmers assigned to the project.
    """
    releases: List[Release] = field(default_factory=list)
    programmers: List[Programmer] = field(default_factory=list)


    def print_plan(self) -> None:
        pass
