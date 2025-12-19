from __future__ import annotations
from dataclasses import dataclass
from typing import List

MAX_PRIORITY = 9

@dataclass(frozen=True) # immutable class for batter performance
class Task:
    """
    Represents a task within the project.

    Attributes:
        cost: Time spent on this task in minutes.
        priority: priority 1-8 (1 = highest, 8 = lowest)
        dependencies: List of other tasks that must be completed before this task.
    """
    id: int
    name: str
    cost: int
    priority: int
    dependencies: List[Task]
    release : int = 0
