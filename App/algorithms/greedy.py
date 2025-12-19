from typing import Tuple, List

from release import Release
from solution import Solution
from programmer import PROGRAMMING_HOURS_IN_WORK_DAY
from task import Task


def fix_dependencies(tasks: List[Task]) -> List[Task]:
    """
    Reorder tasks so that each task appears after its dependencies,
    using repeated swaps until stable.
    """
    max_iterations = len(tasks) * len(tasks)
    for _ in range(max_iterations):
        changed = False
        task_index = {task.id: i for i, task in enumerate(tasks)}
        for i, task in enumerate(tasks):
            for dep in task.dependencies:
                dep_id = dep.id
                if dep_id not in task_index:
                    continue
                dep_index = task_index[dep_id]

                if dep_index > i:
                    tasks[i], tasks[dep_index] = tasks[dep_index], tasks[i]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            break

    return tasks


def greedy(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release]
) -> Solution:
    solution = Solution().initialize(programmers_specs, [], "empty")
    programmer_hours = [0.0] * len(programmers_specs)
    total_capacity_minutes = sum(r.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60 for r in releases)

    sorted_tasks = sorted(tasks, key=lambda t: (t.priority, t.cost))
    sorted_tasks = fix_dependencies(sorted_tasks)

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
