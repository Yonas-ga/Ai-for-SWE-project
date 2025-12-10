from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True) # immutable class for batter performance
class Task:
    """
    Represents a task within the project.

    Attributes:
        cost: Time spent on this task in minutes.
        priority: priority 1-5 (1 = highest, 5 = lowest)
        dependencies: List of other tasks that must be completed before this task.
    """
    id: int
    name: str
    cost: int
    priority: int
    dependencies: List[Task]

    def __str__(self) -> str:
        dep_ids = [t.id for t in self.dependencies]
        return (
            f"Task(id={self.id}, name='{self.name}', cost={self.cost}, "
            f"priority={self.priority}, dependencies={dep_ids})"
        )
