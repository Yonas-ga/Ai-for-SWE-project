from typing import List, Tuple
from solution import Solution
from task import Task
from release import Release
from programmer import PROGRAMMING_HOURS_IN_WORK_DAY
import statistics

def compare_release_plans(solution: Solution, tasks: List[Task], releases: List[Release]) -> dict:
    """
    Compare release plans based on multiple metrics:
    - sum_priorities: Total priority score of completed tasks
    - high_priority_ratio: Percentage of high-priority tasks (1-3) completed
    - total_work_hours: Total hours needed to complete all assigned tasks
    - programmer_variance: Variance in workload distribution among programmers
    """
    
    # Calculate sum of priorities for all assigned tasks
    sum_priorities = 0
    high_priority_count = 0
    total_task_count = 0
    
    for programmer in solution.programmers:
        for task_id in programmer.work_plan:
            task = tasks[task_id]
            sum_priorities += (10 - task.priority) 
            if task.priority <= 3:
                high_priority_count += 1
            total_task_count += 1
    
    # Calculate high-priority ratio
    high_priority_ratio = (high_priority_count / total_task_count * 100) if total_task_count > 0 else 0
    
    # Calculate total work hours needed
    programmer_hours = []
    for programmer in solution.programmers:
        hours = 0.0
        for task_id in programmer.work_plan:
            task = tasks[task_id]
            hours += task.cost / programmer.efficiency / 60 
        programmer_hours.append(hours)
    
    total_work_hours = sum(programmer_hours)
    max_programmer_hours = max(programmer_hours) if programmer_hours else 0
    
    # Calculate programmer workload variance
    if len(programmer_hours) > 1:
        workload_variance = statistics.variance(programmer_hours)
        workload_std_dev = statistics.stdev(programmer_hours)
    else:
        workload_variance = 0.0
        workload_std_dev = 0.0
    
    # Calculate estimated total release date (in days)
    total_capacity_minutes = sum(r.working_days * PROGRAMMING_HOURS_IN_WORK_DAY * 60 for r in releases)
    total_capacity_hours = total_capacity_minutes / 60
    estimated_releases_needed = (max_programmer_hours / PROGRAMMING_HOURS_IN_WORK_DAY) if max_programmer_hours > 0 else 0
    
    return {
        "sum_priorities": sum_priorities,
        "high_priority_ratio": round(high_priority_ratio, 2),
        "high_priority_count": high_priority_count,
        "total_tasks_assigned": total_task_count,
        "total_work_hours": round(total_work_hours, 2),
        "max_programmer_hours": round(max_programmer_hours, 2),
        "workload_variance": round(workload_variance, 2),
        "workload_std_dev": round(workload_std_dev, 2),
        "estimated_release_days": round(estimated_releases_needed, 2),
        "programmer_workloads": {p.name: round(h, 2) for p, h in zip(solution.programmers, programmer_hours)}
    }


def print_comparison(metrics: dict, algorithm_name: str):
    """Pretty print comparison metrics for a release plan."""
    print(f"\n{'='*60}")
    print(f"Release Plan Analysis: {algorithm_name}")
    print(f"{'='*60}")
    print(f"Sum of Priorities:           {metrics['sum_priorities']}")
    print(f"High Priority Ratio:         {metrics['high_priority_ratio']}% ({metrics['high_priority_count']}/{metrics['total_tasks_assigned']} tasks)")
    print(f"Total Work Hours:            {metrics['total_work_hours']} hours")
    print(f"Max Programmer Hours:        {metrics['max_programmer_hours']} hours")
    print(f"Workload Variance:           {metrics['workload_variance']}")
    print(f"Workload Std Dev:            {metrics['workload_std_dev']}")
    print(f"Estimated Release Days:      {metrics['estimated_release_days']} days")
    print(f"\nProgrammer Workloads:")
    for prog_name, hours in metrics['programmer_workloads'].items():
        print(f"  {prog_name:15}: {hours} hours")
    print(f"{'='*60}\n")

from load_data import *
from algorithms.genetic import genetic
from algorithms.hill_climbing import hill_climbing
from algorithms.greedy import greedy
from algorithms.fitness_function import fitness_function
from algorithms.slow_release_ga import call_slow_genetic

if __name__ == '__main__':
    tasks = load_tasks_from_file('data/ASF Jira 2025-12-08T08_13_21+0000.csv')
    programmers = load_programmers_specs_from_file('data/sample_programmers.csv')
    releases = load_releases_from_file('data/sample_releases.csv')
    
    algorithms_to_run = ['greedy', 'hill_climbing', 'genetic', 'slow_release_GA']
    
    results = {}  
    
    # Run all selected algorithms
    for algo_name in algorithms_to_run:
        print(f"\n{'#'*60}")
        print(f"Running {algo_name.upper()} algorithm...")
        print(f"{'#'*60}")
        
        try:
            match algo_name:
                case 'greedy':
                    solution = greedy(tasks, programmers, releases)
                case 'hill_climbing':
                    solution = hill_climbing(tasks, programmers, releases)
                case 'genetic':
                    solution = genetic(tasks, programmers, releases)
                case 'slow_release_GA':
                    solution = call_slow_genetic(tasks, programmers, releases)
                case _:
                    raise ValueError(f'Unknown algorithm {algo_name}')
            
            if solution:
                solution.print_solution(tasks, releases)
                
                # Calculate metrics and fitness
                metrics = compare_release_plans(solution, tasks, releases)
                fitness = fitness_function(solution, tasks, releases)
                metrics['fitness'] = round(fitness, 2)
                
                # Store results
                results[algo_name] = metrics
                
                # Print detailed comparison
                print_comparison(metrics, algo_name)
                print(f"Fitness: {metrics['fitness']}\n")
            else:
                print(f"No solution found for {algo_name}")
                
        except Exception as e:
            print(f"Error running {algo_name}: {str(e)}\n")
    
    # Print summary comparison if multiple algorithms were run
    if len(algorithms_to_run) > 1:
        print(f"\n{'='*140}")
        print("SUMMARY COMPARISON - ALL ALGORITHMS")
        print(f"{'='*140}\n")
        
        header = f"{'Algorithm':<15} {'Fitness':<10} {'Sum Prio':<10} {'Hi Prio %':<10} {'Tot Hours':<10} {'Max Hours':<10} {'Var':<8} {'StdDev':<8} {'Est Days':<8}"
        print(header)
        print(f"{'-'*140}")
        
        for algo_name in algorithms_to_run:
            if algo_name in results:
                m = results[algo_name] 
                
                row = f"{algo_name:<15} {m['fitness']:<10} {m['sum_priorities']:<10} {m['high_priority_ratio']:<10} {m['total_work_hours']:<10} {m['max_programmer_hours']:<10} {m['workload_variance']:<8} {m['workload_std_dev']:<8} {m['estimated_release_days']:<8}"
                print(row)
        print(f"{'='*140}\n")
        
        if results:
            best_algo = max(results.keys(), key=lambda x: results[x]['fitness'])
            print(f"Best Algorithm based on Fitness: {best_algo}")