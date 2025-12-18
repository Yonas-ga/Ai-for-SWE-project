from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from task import MAX_PRIORITY

PROGRAMMING_HOURS_IN_WORK_DAY = 6


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

    def evaluate_work_plan(self, tasks, releases) -> tuple[List[int], float, bool, List[int]]:
        priority_per_release = []
        time_left = 0.0
        plan_index = 0
        task_to_release = {}
        for i, release in enumerate(releases):
            release_priority = 0
            time_left += release.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60
            while plan_index < len(self.work_plan):
                task = tasks[self.work_plan[plan_index]]
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

    def print_work_plan(self, tasks, releases) -> None:
        print("-----------------------------")
        print(f"Programmer: {self.name}, Efficiency: {self.efficiency}, Work Plan:")
        time_left = 0.0
        plan_index = 0
        for release in releases:
            time_left += release.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60
            print(f" Release from {release.start_day} to {release.end_date}, "
                  f"Working mins: {release.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60}")
            while plan_index < len(self.work_plan):
                task = tasks[self.work_plan[plan_index]]
                if time_left - (task.cost / self.efficiency) >= 0:
                    print(f"Task {task.id}: priority {task.priority}, cost {task.cost} minutes")
                    time_left -= task.cost / self.efficiency
                    plan_index += 1
                else:
                    break
