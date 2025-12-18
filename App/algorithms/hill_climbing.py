import random
from typing import List, Tuple

from App.release import Release
from App.task import Task
from App.solution import Solution
from App.algorithms.fitness_function import fitness_function


def hill_climbing(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release],
        init_strategy: str = "priority_div_cost",
        max_iterations: int = 200,
        swap_tries: int = 50,
        move_tries: int = 50,
) -> Solution:
    def random_swap_neighbor(individual: Solution) -> Solution:
        neighbour = individual.clone()
        candidates = [p for p in neighbour.programmers if len(p.work_plan) >= 2]
        if not candidates:
            return neighbour
        prog = random.choice(candidates)
        idx1 = random.randrange(len(prog.work_plan))
        idx2 = random.randrange(len(prog.work_plan))
        prog.work_plan[idx1], prog.work_plan[idx2] = prog.work_plan[idx2], prog.work_plan[idx1]
        return neighbour

    def random_move_neighbor(individual: Solution) -> Solution:
        neighbour = individual.clone()
        src_candidates = [p for p in neighbour.programmers if len(p.work_plan) >= 1]
        if len(src_candidates) < 1 or len(neighbour.programmers) < 2:
            return neighbour

        prog1 = random.choice(src_candidates)
        prog2 = random.choice([p for p in neighbour.programmers if p is not prog1])

        task_idx = random.randrange(len(prog1.work_plan))
        task_id = prog1.work_plan.pop(task_idx)
        insert_idx = random.randrange(len(prog2.work_plan) + 1)
        prog2.work_plan.insert(insert_idx, task_id)
        return neighbour

    # Initialization
    current = Solution().initialize(programmers_specs, tasks.copy(), init_strategy)
    current_fitness = fitness_function(current, tasks, releases)
    best = current.clone()
    best_fitness = current_fitness

    print("HC initial fitness:", round(best_fitness, 2))

    # Hill climbing
    for it in range(max_iterations):
        best_neighbor = None
        best_neighbor_fitness = current_fitness

        # Try swaping tasks inside programmers work plans
        for _ in range(swap_tries):
            neighbour = random_swap_neighbor(current)
            fit = fitness_function(neighbour, tasks, releases)
            if fit > best_neighbor_fitness:
                best_neighbor_fitness = fit
                best_neighbor = neighbour

        # Try moving tasks between programmers
        for _ in range(move_tries):
            neighbour = random_move_neighbor(current)
            fit = fitness_function(neighbour, tasks, releases)
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
            print(f"HC stopped at iter {it}: local optimum fitness = {round(current_fitness, 2)}")
            break

    for t in best.programmers:
        t.print_work_plan(tasks, releases)
    print("HC best fitness:", round(best_fitness, 2))
    return best
