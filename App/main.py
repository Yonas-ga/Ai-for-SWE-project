import argparse

from App.load_data import *
from App.algorithms.genetic import genetic

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--algorithm', type=str, required=False, default='genetic')
    parser.add_argument('-t', '--tasks_file', type=str, required=False, default='')
    parser.add_argument('-r', '--releases_file', type=str, required=False, default='')
    parser.add_argument('-p', '--programmers_file', type=str, required=False, default='')

    args = parser.parse_args()

    tasks = load_tasks_from_file(args.tasks_file)
    programmers = load_programmers_from_file(args.programmers_file)
    releases = load_releases_from_file(args.releases_file)

    match args.algorithm:
        case 'genetic':
            genetic(tasks, programmers, releases)
        case _:
            raise ValueError(f'Unknown algorithm {args.algorithm}')

