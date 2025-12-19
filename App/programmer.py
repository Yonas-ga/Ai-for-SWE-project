from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from task import MAX_PRIORITY
from style import Colors

PROGRAMMING_HOURS_IN_WORK_DAY = 6


@dataclass
class Programmer:
    """
    Represents a programmer in the team.
    """
    name: str
    efficiency: float = 1.0
    work_plan: List[int] = field(default_factory=list)

    def add_task(self, task_id: int) -> None:
        self.work_plan.append(task_id)

    def evaluate_work_plan(self, tasks, releases, active_ids=None):
        priority_per_release = []
        time_left = 0.0
        plan_index = 0
        task_to_release = {}
        for i, release in enumerate(releases):
            release_priority = 0
            time_left += release.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60
            while plan_index < len(self.work_plan):
                task_id = self.work_plan[plan_index]
                if active_ids != None and task_id not in active_ids:
                    plan_index += 1
                    continue
                task = tasks[task_id]
                if time_left - (task.cost / self.efficiency) >= 0:
                    time_left -= task.cost / self.efficiency
                    release_priority += MAX_PRIORITY + 1 - task.priority
                    task_to_release[task.id] = i
                    plan_index += 1
                else:
                    break
            priority_per_release.append(release_priority)

        overflowing = plan_index != len(self.work_plan)
        return priority_per_release, time_left, overflowing, task_to_release