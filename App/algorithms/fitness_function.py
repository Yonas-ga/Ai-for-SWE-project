from statistics import stdev
from typing import List

from release import Release
from task import Task
from solution import Solution

DEPENDENCY_PENALTY = 500
OVERFLOW_PENALTY = 10000
IMBALANCE_WEIGHT = 20  

def fitness_function(individual: Solution, tasks: List[Task], releases: List[Release], debug: bool = False) -> float:
    fitness = 0
    time_lefts = []
    assigned_times = []
    global_task_to_release = {}
    for prog in individual.programmers:
        priority_per_release, time_left, overflowing, task_to_release = prog.evaluate_work_plan(tasks, releases)
        for task_id, i in task_to_release.items():
            global_task_to_release[task_id] = i
        if overflowing:
            fitness -= OVERFLOW_PENALTY
        time_lefts.append(time_left)
        total_assigned = sum((tasks[i].cost / prog.efficiency) for i in task_to_release.keys())
        assigned_times.append(total_assigned)
        num_of_releases = len(priority_per_release)
        for i in range(num_of_releases):
            fitness += priority_per_release[i] * (2 ** (num_of_releases - i))

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
    
    stdev_assigned = stdev(assigned_times) 
    mean_assigned = sum(assigned_times) / len(assigned_times)
    imbalance_ratio = (max(assigned_times) / mean_assigned) 

    if debug:
        print(
            "fitness:", round(fitness, 2),
            "stdev_assigned:", round(stdev_assigned, 2),
            "imbalance_ratio:", round(imbalance_ratio, 2),
            "dep_violations:", dep_violations,
        )

    fitness -= IMBALANCE_WEIGHT * stdev_assigned

    return fitness
