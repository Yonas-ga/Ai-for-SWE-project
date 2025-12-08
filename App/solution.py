from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from programmer import Programmer
from .task import Task


@dataclass
class Solution:
    programmers: List[Programmer] = field(default_factory=list)

    def initialize(self, programmer_specs: List[tuple[str, float]], tasks: List[Task],
                   init_strategy="random") -> Solution:
        self.programmers = [Programmer(name=name, efficiency=efficiency) for name, efficiency in programmer_specs]

        #TODO: maybe try more strategies for initialization
        match init_strategy:
            case "random":
                random.shuffle(tasks)
            case "priority_cost":
                tasks = sorted(tasks, key=lambda t: (-t.priority, t.cost))
            case "priority_div_cost":
                tasks = sorted(tasks, key=lambda t: (6 - t.priority / t.cost))  # TODO: check if woks as intended
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
        flat: List[int] = []
        for p in self.programmers:
            flat.extend(p.work_plan)
        return flat

