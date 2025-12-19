import random
from typing import List, Tuple

from release import Release
from task import Task
from solution import Solution
from algorithms.fitness_function import fitness_function


def slow_genetic(
        tasks: List[Task],
        programmers_specs: List[Tuple[str, float]],
        releases: List[Release],
        init_strategy="random",
        population_size: int = 250,
        generations: int = 100,
        crossover_rate: float = 0.6,
        mutation_rate: float = 0.5,
        tournament_size: int = 15,
        initial_solution = None,
        current_release = 0,
        active_id=None
) -> Solution:
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

    def crossover(p1: int, p2: int) -> Tuple[Solution, Solution]: #this is a simpler crossover
        if random.random() > crossover_rate:
            return population[p1].clone(), population[p2].clone()

        child1 = population[p1].clone()
        child2 = population[p2].clone()
        prog1 = random.choice(child1.programmers)
        prog2 = random.choice(child2.programmers)
        free1 =  [i for i, t in enumerate(prog1.work_plan) if t not in frozen_tasks]
        free2 =  [i for i, t in enumerate(prog2.work_plan) if t not in frozen_tasks]
        
        if free1 == [] or free2 == []:
            return child1, child2
        i1 = random.choice(free1)
        i2 = random.choice(free2)
        
        prog1.work_plan[i1], prog2.work_plan[i2] = prog2.work_plan[i2],prog1.work_plan[i1]
        
        return child1, child2

    def mutate(individual: Solution) -> Solution:
        if random.random() > mutation_rate:
            return individual
        # backup = individual.clone()
        prog1 = random.choice(individual.programmers)
        movable = [i for i,t in enumerate(prog1.work_plan) if t not in frozen_tasks]
        if not movable:
            return individual
        if random.random() > 0.5:
            # swap two tasks in a programmer's work plan
            if len(movable) <2:
                return individual
            idx1 = random.choice(movable)
            idx2 = random.choice(movable)
            prog1.work_plan[idx1], prog1.work_plan[idx2] = prog1.work_plan[idx2], prog1.work_plan[idx1]
        else:
            # move a task from one programmer to another
            prog2 = random.choice([p for p in individual.programmers if p is not prog1])
            task1 = prog1.work_plan.pop(random.choice(movable))
            prog2.work_plan.insert(random.randrange(len(prog2.work_plan)), task1)
        return individual

    # Initialize
    frozen_tasks = set()
    if initial_solution != None:
        for prog in initial_solution.programmers:
            _, _, _, task_to_release = prog.evaluate_work_plan(tasks, releases)
            for task_id, i in task_to_release.items():
                if i < current_release:
                    frozen_tasks.add(task_id)
    
    population = []
    fitness = []
    best_fitness = float('-inf')
    best = None

    if initial_solution == None:
        for _ in range(population_size):
            individual = Solution().initialize(programmers_specs, tasks.copy(), init_strategy)
            population.append(individual)
            fit = fitness_function(individual, tasks, releases, active_ids=active_id)
            fitness.append(fit)
            if fit > best_fitness:
                best_fitness = fit
                best = individual
    else:
        for _ in range(population_size):
            individual = mutate(initial_solution.clone())
            population.append(individual)
            fit = fitness_function(individual, tasks, releases, active_ids=active_id)
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
            fitness[i] = fitness_function(population[i], tasks, releases, active_ids=active_id)
            if fitness[i] > best_fitness:
                best_fitness = fitness[i]
                best = population[i].clone()

        if  gen % 10 == 0:
            print(f"Generation: {gen}, best fitness: {round(best_fitness, 2)}")

    return best

def call_slow_genetic(tasks: List[Task],programmers_specs: List[Tuple[str, float]],releases: List[Release],):
    weights = [1 ** i for i in range(len(releases))]
    total = sum(weights)
    probs = [w/total for w in weights]
    split_tasks = [[] for _ in range(len(releases))]
    for t in tasks:
        x = random.choices(range(len(releases)), probs)[0]
        split_tasks[x].append(t)
    
    solution = None
    
    for i in range(len(releases)):
        current_tasks = [t for j in range(i+1) for t in split_tasks[j]]
        active = {t.id for t in current_tasks}
        solution = slow_genetic(tasks, programmers_specs, releases, initial_solution = solution, current_release = i, active_id= active)
    return solution