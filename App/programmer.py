from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Programmer:
    """
    Represents a programmer in the team.

    Attributes:
        name: Programmer's name.
        efficiency: Productivity multiplier (man-hours completed per real hour).
        work_plan: Ordered list of task IDs assigned to this programmer.
    """
    name: str
    efficiency: float = 1.0
    work_plan: List[int] = field(default_factory=list)

    def add_task(self, task_id: int) -> None:
        self.work_plan.append(task_id)

    def add_task_at(self, index: int, task_id: int) -> None:
        self.work_plan.insert(index, task_id)

    def get_task_at(self, index: int) -> int:
        if index < len(self.work_plan):
            return self.work_plan[index]
        else:
            return self.work_plan[-1]
