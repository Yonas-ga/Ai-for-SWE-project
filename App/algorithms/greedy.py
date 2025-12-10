from typing import List, Tuple

from App.release import Release
from App.task import Task
from App.solution import Solution
from App.programmer import PROGRAMMING_HOURS_IN_WORK_DAY

def greedy(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release]
) -> Solution:
    solution = Solution().initialize(programmers_specs, [], "empty")

    # Already assigned task hours
    programmer_hours = [0.0] * len(programmers_specs)
    total_capacity_minutes = sum(r.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60 for r in releases)

    # 1 Priority, 2 Cost
    sorted_tasks = sorted(tasks, key=lambda t: (t.priority, t.cost))

    for task in sorted_tasks:
        best_programmer_id = -1
        earliest_finish_time = float('inf')

        # Find programmer who can finish task quickest
        for i, prog in enumerate(solution.programmers):
            task_done_at = programmer_hours[i] + task.cost / prog.efficiency

            if task_done_at < earliest_finish_time:
                earliest_finish_time = task_done_at
                best_programmer_id = i

        # check if task is done by last planned release, else drop task
        if earliest_finish_time <= total_capacity_minutes:
            chosen_prog = solution.programmers[best_programmer_id]
            
            chosen_prog.add_task(task.id)
            programmer_hours[best_programmer_id] += (task.cost / chosen_prog.efficiency)

    return solution