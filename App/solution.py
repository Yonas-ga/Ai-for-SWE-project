from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from App.programmer import Programmer
from App.task import Task, MAX_PRIORITY_PLUS_ONE


@dataclass
class Solution:
    programmers: List[Programmer] = field(default_factory=list)

    def initialize(self, programmer_specs: List[tuple[str, float]], tasks: List[Task],
                   init_strategy="random") -> Solution:
        self.programmers = [Programmer(name=name, efficiency=efficiency) for name, efficiency in programmer_specs]

        match init_strategy:
            case "empty":
                return self
            case "random":
                random.shuffle(tasks)
            case "priority_cost":
                tasks = sorted(tasks, key=lambda t: (-t.priority, t.cost))
            case "priority_div_cost":
                tasks = sorted(tasks, key=lambda t: ((MAX_PRIORITY_PLUS_ONE - t.priority) / t.cost))
            case _:
                raise ValueError(f"Unknown initialization strategy: {init_strategy}")

        for task in tasks:
            random.choice(self.programmers).add_task(task.id)
        return self

    def clone(self) -> Solution:
        """Copy: programmers and their work_plans."""
        new_programmers: List[Programmer] = []
        for p in self.programmers:
            new_p = Programmer(
                name=p.name,
                efficiency=p.efficiency,
                work_plan=p.work_plan.copy()
            )
            new_programmers.append(new_p)
        return Solution(programmers=new_programmers)

    def flatten(self) -> List[int]:
        flat = []
        for p in self.programmers:
            flat.extend(p.work_plan)
        return flat

