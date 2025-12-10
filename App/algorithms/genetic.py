import random
from statistics import stdev
from typing import List, Tuple

from App.release import Release
from App.task import Task
from App.solution import Solution


def genetic(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release],
        init_strategy="priority_cost",
        population_size: int = 100,
        generations: int = 60,
        crossover_rate: float = 0.7,
        mutation_rate: float = 0.4,
        tournament_size: int = 3,
) -> Solution:
    def fitness_function(individual: Solution, debug: bool = False) -> float:
        fitness = 0
        time_lefts = []
        global_task_to_release = {}
        for prog in individual.programmers:
            priority_per_release, time_left, overflowing, task_to_release = prog.evaluate_work_plan(tasks, releases)
            for task_id, i in task_to_release.items():
                global_task_to_release[task_id]=i
            if overflowing:
                fitness -= 10000
            time_lefts.append(time_left)
            num_of_releases = len(priority_per_release)
            for i in range(num_of_releases):
                fitness += priority_per_release[i] * (2 ** (num_of_releases - i)) # TODO: might need tuning
                
        DEPENDENCY_PENALTY = 50
        dep_violations = 0
        for t in tasks:
            t_release = global_task_to_release.get(t.id, None)
            if t_release is None:
                continue
            for child in t.dependencies:
                child_release = global_task_to_release.get(child.id, None)
                if child_release is None or child_release > t_release:
                    dep_violations +=1
        
        fitness -= dep_violations*DEPENDENCY_PENALTY
                    

        if debug:
            print("fitness without penalty:", fitness, "stdev penalty:", round(stdev(time_lefts)), "dep_violations:", dep_violations)

        # penalize unbalanced workloads
        fitness -= stdev(time_lefts)  # TODO: might need tuning
        return fitness


    def select() -> int:
        selected = random.randrange(0, len(population))
        for _ in range(tournament_size - 1):
            candidate = random.randrange(0, len(population))
            if fitness[candidate] > fitness[selected]:
                selected = candidate
        return selected

    def apply_swap(indiv, src_list, dst_list):
        for prog in indiv.programmers:
            for i in range(len(prog.work_plan)):
                for j in range(len(src_list)):
                    if prog.work_plan[i] == src_list[j]:
                        prog.work_plan[i] = dst_list[j]

    def crossover(p1: int, p2: int) -> Tuple[Solution, Solution]:
        if random.random() > crossover_rate:
            return population[p1].clone(), population[p2].clone()

        child1 = population[p1].clone()
        child2 = population[p2].clone()
        prog1 = random.choice(child1.programmers)
        prog2 = random.choice(child2.programmers)
        if len(prog1.work_plan) < 2 or len(prog2.work_plan) < 2:
            return child1, child2

        # choose random segment length and start, end indices
        max_len = min(len(prog1.work_plan), len(prog2.work_plan))
        seg_len = random.randint(1, max_len)
        start1 = random.randint(0, len(prog1.work_plan) - seg_len)
        start2 = random.randint(0, len(prog2.work_plan) - seg_len)
        end1 = start1 + seg_len
        end2 = start2 + seg_len
        # get segments
        segment1 = prog1.work_plan[start1:end1]
        segment2 = prog2.work_plan[start2:end2]

        # prepare swap mapping
        swap1 = []
        swap2 = segment2.copy()
        for task in segment1:
            if task not in swap2:
                swap1.append(task)
            else:
                swap2.remove(task)
        apply_swap(child1, swap2, swap1)
        apply_swap(child2, swap1, swap2)

        # finally, swap the segments
        prog1.work_plan[start1:end1] = segment2
        prog2.work_plan[start2:end2] = segment1

        # TODO: safety check, remove later
        parent_tasks = sorted(population[p1].flatten())
        if sorted(child1.flatten()) != parent_tasks:
            raise ValueError("Child1 lost or duplicated tasks during crossover.")
        if sorted(child2.flatten()) != parent_tasks:
            raise ValueError("Child2 lost or duplicated tasks during crossover.")
        return child1, child2

    def mutate(individual: Solution) -> Solution:
        if random.random() > mutation_rate:
            return individual
        beckup = individual.clone()
        if random.random() > 0.5:
            # swap two tasks in a programmer's work plan
            prog = random.choice(individual.programmers)
            idx1 = random.randrange(len(prog.work_plan))
            idx2 = random.randrange(len(prog.work_plan))
            prog.work_plan[idx1], prog.work_plan[idx2] = prog.work_plan[idx2], prog.work_plan[idx1]
        else:
            # move a task from one programmer to another
            prog1, prog2 = random.sample(individual.programmers, 2)
            task1 = prog1.work_plan.pop(random.randrange(len(prog1.work_plan)))
            prog2.work_plan.insert(random.randrange(len(prog2.work_plan)), task1)

        if sorted(individual.flatten()) != sorted(beckup.flatten()):
            raise ValueError("Child1 lost or duplicated tasks during mutate.")
        return individual

    # Initialize
    population = []
    fitness = []
    best_fitness = float('-inf')
    best = None

    for _ in range(population_size):
        individual = Solution().initialize(programmers_specs, tasks.copy(), init_strategy)
        population.append(individual)
        fit = fitness_function(individual)
        fitness.append(fit)
        if fit > best_fitness:
            best_fitness = fit
            best = individual

    # Evolve population
    for gen in range(generations):
        new_population = []
        while len(new_population) < population_size:
            parent1 = select()
            parent2 = select()
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.append(child1)
            new_population.append(child2)
        population = new_population

        for i in range(population_size):
            fitness[i] = fitness_function(population[i])
            if fitness[i] > best_fitness:
                best_fitness = fitness[i]
                best = population[i].clone()
                # DEBUG
                print(gen, "fitness:", round(best_fitness,2))

    # DEBUG
    #for t in best.programmers:
        #t.print_work_plan(tasks, releases)

    fitness_function(best, True)
    print(round(best_fitness,2))
    return best
