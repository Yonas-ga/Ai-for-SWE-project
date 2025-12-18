import argparse

from load_data import *
from algorithms.genetic import genetic
from algorithms.hill_climbing import hill_climbing
from algorithms.greedy import greedy
from algorithms.fitness_function import fitness_function

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--algorithm', type=str, required=False, default="genetic") # "hill_climbing", "greedy"
    parser.add_argument('-t', '--tasks_file', type=str, required=False, default='data/ASF Jira 2025-12-08T08_13_21+0000.csv')
    parser.add_argument('-r', '--releases_file', type=str, required=False, default='data/sample_releases.csv')
    parser.add_argument('-p', '--programmers_file', type=str, required=False, default='data/sample_programmers.csv')

    args = parser.parse_args()

    tasks = load_tasks_from_file(args.tasks_file)
    programmers = load_programmers_specs_from_file(args.programmers_file)
    releases = load_releases_from_file(args.releases_file)
    match args.algorithm:
        case 'greedy':
            solution = greedy(tasks, programmers, releases)
        case 'hill_climbing':
            solution = hill_climbing(tasks, programmers, releases)
        case 'genetic':
            solution = genetic(tasks, programmers, releases)
        case _:
            raise ValueError(f'Unknown algorithm {args.algorithm}')

    if solution:
        solution.print_solution(tasks, releases)

    fitness = fitness_function(solution, tasks, releases)
    print(f"\nFitness of release plan found by {args.algorithm}: {round(fitness, 2)}")
