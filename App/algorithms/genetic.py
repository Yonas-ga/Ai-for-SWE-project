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
        init_strategy="random",
        population_size: int = 40,
        generations: int = 5,
        crossover_rate: float = 0.6,
        mutation_rate: float = 0.7,
        tournament_size: int = 3,
) -> Solution:
    def fitness_function(individual: Solution, debug: bool = False) -> float:
        fitness = 0
        time_lefts = []
        for prog in individual.programmers:
            priority_per_release, time_left, overflowing = prog.evaluate_work_plan(tasks, releases)
            if overflowing:
                fitness -= 1000  # TODO: not sure what to do when work plan overflows
            time_lefts.append(time_left)
            num_of_releases = len(priority_per_release)
            for i in range(num_of_releases):
                fitness += priority_per_release[i] * (num_of_releases - i) # TODO: might need tuning

        if debug:
            print("fitness without penalty:", fitness, "time_lefts:", time_lefts, "stdev penalty:", stdev(time_lefts))

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

    from typing import Tuple

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

        # get segments and swap them
        segment1 = prog1.work_plan[start1:end1]
        segment2 = prog2.work_plan[start2:end2]
        prog1.work_plan[start1:end1] = segment2
        prog2.work_plan[start2:end2] = segment1

        # fix duplicates / missing tasks
        swap = [[], []]
        for task in segment1:
            if task not in segment2:
                swap[0].append(task)
            else:
                segment2.remove(task)
        swap[1] = segment2

        # TODO: replace with function
        for prog in child1.programmers:
            for i in range(len(prog.work_plan)):
                for task in swap[1]:
                    if prog.work_plan[i] == task:
                        prog.work_plan[i] = swap[0]

        for prog in child2.programmers:
            for i in range(len(prog.work_plan)):
                for task in swap[0]:
                    if prog.work_plan[i] == task:
                        prog.work_plan[i] = swap[1]

        # TODO: safety check, remove later
        if sorted(child1.flatten) != sorted(child2.flatten):
            raise ValueError("Parents must contain the same multiset of tasks for crossover.")
        return child1, child2

    def mutate(individual: Solution) -> Solution:
        if random.random() > mutation_rate:
            return individual

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
        return individual

    # Initialize
    population = []
    fitness = []
    best_fitness = float('-inf')
    best = None

    for _ in range(population_size):
        individual = Solution().initialize(programmers_specs, tasks, init_strategy)
        population.append(individual)
        fit = fitness_function(individual)
        fitness.append(fit)
        if fit > best_fitness:
            best_fitness = fit
            best = individual

    # Evolve population
    for gen in range(generations):
        new_population = []
        for _ in range(population_size):
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
                best = population[i]
                # DEBUG
                print(gen, "fitness:", fitness_function(best, True))

    # DEBUG
    print(best)
    fitness_function(best, True)

    return best
