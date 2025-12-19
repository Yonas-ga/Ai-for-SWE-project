from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from style import Colors
from programmer import Programmer, PROGRAMMING_HOURS_IN_WORK_DAY
from task import Task, MAX_PRIORITY


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
                tasks = sorted(tasks, key=lambda t: (t.priority, t.cost))
            case "priority_div_cost":
                tasks = sorted(tasks, key=lambda t: ((MAX_PRIORITY + 1 - t.priority) / t.cost))
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

    def print_solution(self, tasks, releases):
        # We track where each programmer is in their own work_plan list
        programmer_progress = {p.name: 0 for p in self.programmers}

        for i, release in enumerate(releases):
            print(
                f"{Colors.BOLD}{Colors.HEADER}Release {i + 1}, from {release.start_day} to {release.end_date}{Colors.ENDC}")

            # Calculate total minutes available in this release (real time)
            release_minutes = release.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60

            for p in self.programmers:
                # Give each programmer a fresh time budget for this release
                time_budget = release_minutes

                # Start the line: "Tomas: "
                row_output = f"{p.name:10}: "

                current_idx = programmer_progress[p.name]

                while current_idx < len(p.work_plan):
                    task_id = p.work_plan[current_idx]
                    task = tasks[task_id]

                    # Calculate cost adjusted for this programmer's efficiency
                    real_cost = task.cost / p.efficiency

                    if time_budget - real_cost >= 0:
                        # Task fits in this release
                        color = Colors.get_priority_color(task.priority)

                        # Formatting: |  Issue X  |
                        # The ^13 centers the text.
                        task_str = f" Issue {task.id} "
                        row_output += f"{color}|{task_str:^13}|{Colors.ENDC}"

                        time_budget -= real_cost
                        current_idx += 1
                    else:
                        # Task does not fit in this release, wait for next one
                        break

                # Save the progress index for the next release loop
                programmer_progress[p.name] = current_idx
                print(row_output)

            # Print a separator between releases
            print("-" * 60)