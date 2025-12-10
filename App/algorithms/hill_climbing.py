import random
from statistics import stdev, StatisticsError
from typing import List, Tuple

from App.release import Release
from App.task import Task
from App.solution import Solution

DEPENDENCY_PENALTY = 500


def hill_climbing(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release],
        init_strategy: str = "priority_cost",
        max_iterations: int = 200,
        swap_tries: int = 50,
        move_tries: int = 50,
) -> Solution:
    def fitness_function(individual: Solution, debug: bool = False) -> float:
        fitness = 0.0
        time_lefts: List[float] = []
        global_task_to_release: dict[int, int] = {}

        for prog in individual.programmers:
            priority_per_release, time_left, overflowing, task_to_release = prog.evaluate_work_plan(tasks, releases)

            # remember release index for each task
            for task_id, i in task_to_release.items():
                global_task_to_release[task_id] = i

            if overflowing:
                fitness -= 10000  # strong penalty for overflow

            time_lefts.append(time_left)
            num_of_releases = len(priority_per_release)

            # reward priority earlier (discounted by 2^(num_releases - i))
            for i in range(num_of_releases):
                fitness += priority_per_release[i] * (2 ** (num_of_releases - i))

        # dependency penalty
        dep_violations = 0
        for t in tasks:
            t_release = global_task_to_release.get(t.id, None)
            if t_release is None:
                continue
            for child in t.dependencies:
                child_release = global_task_to_release.get(child.id, None)
                # child must be in same or earlier release
                if child_release is None or child_release > t_release:
                    dep_violations += 1

        fitness -= dep_violations * DEPENDENCY_PENALTY

        # penalize unbalanced workloads
        fitness -= stdev(time_lefts)

        if debug:
            print(
                "fitness:", round(fitness, 2),
                "stdev penalty:", round(stdev(time_lefts), 2),
                "dep_violations:", dep_violations,
            )

        return fitness

    def random_swap_neighbor(individual: Solution) -> Solution:
        neighbour = individual.clone()
        # choose programmer with at least 2 tasks
        candidates = [p for p in neighbour.programmers if len(p.work_plan) >= 2]
        if not candidates:
            return neighbour
        prog = random.choice(candidates)
        idx1 = random.randrange(len(prog.work_plan))
        idx2 = random.randrange(len(prog.work_plan))
        prog.work_plan[idx1], prog.work_plan[idx2] = prog.work_plan[idx2], prog.work_plan[idx1]

        # safety: permutation must stay the same
        if sorted(neighbour.flatten()) != sorted(individual.flatten()):
            raise ValueError("Neighbour (swap) lost or duplicated tasks.")
        return neighbour

    def random_move_neighbor(individual: Solution) -> Solution:
        neighbour = individual.clone()
        # choose source programmer with at least 1 task
        src_candidates = [p for p in neighbour.programmers if len(p.work_plan) >= 1]
        if len(src_candidates) < 1 or len(neighbour.programmers) < 2:
            return neighbour

        prog1 = random.choice(src_candidates)
        # destination can be any other programmer
        prog2 = random.choice([p for p in neighbour.programmers if p is not prog1])

        task_idx = random.randrange(len(prog1.work_plan))
        task_id = prog1.work_plan.pop(task_idx)
        insert_idx = random.randrange(len(prog2.work_plan) + 1)
        prog2.work_plan.insert(insert_idx, task_id)
        return neighbour

    # --- Initialization: start from one solution (same as GA init) ---
    current = Solution().initialize(programmers_specs, tasks.copy(), init_strategy)
    current_fitness = fitness_function(current)
    best = current.clone()
    best_fitness = current_fitness

    print("HC initial fitness:", round(best_fitness, 2))

    # --- Hill climbing loop ---
    for it in range(max_iterations):
        best_neighbor = None
        best_neighbor_fitness = current_fitness

        # 1) Try swap neighbours
        for _ in range(swap_tries):
            neighbour = random_swap_neighbor(current)
            fit = fitness_function(neighbour)
            if fit > best_neighbor_fitness:
                best_neighbor_fitness = fit
                best_neighbor = neighbour

        # 2) Try move neighbours
        for _ in range(move_tries):
            neighbour = random_move_neighbor(current)
            fit = fitness_function(neighbour)
            if fit > best_neighbor_fitness:
                best_neighbor_fitness = fit
                best_neighbor = neighbour

        # 3) Decide whether to move to best neighbour
        if best_neighbor is not None and best_neighbor_fitness > current_fitness:
            current = best_neighbor
            current_fitness = best_neighbor_fitness

            if current_fitness > best_fitness:
                best = current.clone()
                best_fitness = current_fitness

            print(f"HC iter {it}: fitness = {round(current_fitness, 2)}")
        else:
            # no improving neighbour → local optimum
            print(f"HC stopped at iter {it}: local optimum fitness = {round(current_fitness, 2)}")
            break

    for t in best.programmers:
        t.print_work_plan(tasks, releases)
    print("HC best fitness:", round(best_fitness, 2))
    return best
