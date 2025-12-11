from statistics import stdev
from typing import List

from App.release import Release
from App.task import Task
from App.solution import Solution

DEPENDENCY_PENALTY = 500
OVERFLOW_PENALTY = 10000


def fitness_function(individual: Solution, tasks: List[Task], releases: List[Release], debug: bool = False) -> float:
    fitness = 0
    time_lefts = []
    global_task_to_release = {}
    for prog in individual.programmers:
        priority_per_release, time_left, overflowing, task_to_release = prog.evaluate_work_plan(tasks, releases)
        for task_id, i in task_to_release.items():
            global_task_to_release[task_id] = i
        if overflowing:
            fitness -= OVERFLOW_PENALTY
        time_lefts.append(time_left)
        num_of_releases = len(priority_per_release)
        for i in range(num_of_releases):
            fitness += priority_per_release[i] * (2 ** (num_of_releases - i))  # TODO: might need tuning

    dep_violations = 0
    for t in tasks:
        t_release = global_task_to_release.get(t.id, None)
        if t_release is None:
            continue
        for child in t.dependencies:
            child_release = global_task_to_release.get(child.id, None)
            if child_release is None or child_release > t_release:
                dep_violations += 1

    fitness -= dep_violations * DEPENDENCY_PENALTY

    if debug:
        print(
            "fitness:", round(fitness, 2),
            "stdev penalty:", round(stdev(time_lefts), 2),
            "dep_violations:", dep_violations,
        )

    # penalize unbalanced workloads
    fitness -= stdev(time_lefts)  # TODO: might need tuning
    return fitness
