import argparse

from load_data import *
from algorithms.genetic import genetic
from algorithms.hill_climbing import hill_climbing
from algorithms.greedy import greedy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--algorithm', type=str, required=False, default="genetic") #default='hill_climbing')
    parser.add_argument('-t', '--tasks_file', type=str, required=False, default='data/ASF Jira 2025-12-08T08_13_21+0000.csv')
    parser.add_argument('-r', '--releases_file', type=str, required=False, default='data/sample_releases.csv')
    parser.add_argument('-p', '--programmers_file', type=str, required=False, default='data/sample_programmers.csv')

    args = parser.parse_args()

    tasks = load_tasks_from_file(args.tasks_file)
    programmers = load_programmers_specs_from_file(args.programmers_file)
    releases = load_releases_from_file(args.releases_file)

    match args.algorithm:
        case 'genetic':
            genetic(tasks, programmers, releases)
            #genetic(tasks[:50], programmers[:4], releases[:3])
        case 'hill_climbing':
            hill_climbing(tasks, programmers, releases)
        case 'greedy':
            greedy(tasks, programmers, releases)
        case _:
            raise ValueError(f'Unknown algorithm {args.algorithm}')

