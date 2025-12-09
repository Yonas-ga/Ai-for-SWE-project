from typing import List, Tuple

from task import Task
from release import Release

import csv
from datetime import datetime

priority_map = {
    "Blocker": 1,
    "Critical": 2,
    "Major": 3,
    "High": 4,
    "Medium": 5,
    "Minor": 6,
    "Low": 7,
    "Trivial": 8,
}

def load_tasks_from_file(file_path: str) -> List[Task]:
    # Get Tasks from the CSV file taken from the Apache JIRA dataset
    if not file_path:
        raise ValueError("tasks_file path is empty.")
    rows = []
    with open(file_path, newline="", encoding="utf-8") as f:
        tmp = csv.DictReader(f)
        for line in tmp:
            issue_key = (line.get("Issue key") or "").strip()
            priority = priority_map.get(line.get("Priority", ""), 4)
            time_spent = float((line.get("Time Spent") or "").strip())
            hours_spent = time_spent/3600
            rows.append((issue_key,hours_spent,priority))
    tasks = []
    for i in range(len(rows)):
        tasks.append(Task(id=i, name=rows[i][0], cost=rows[i][1], priority=rows[i][2], dependencies=[]))
    return tasks


def load_releases_from_file(file_path: str) -> List[Release]:
    # loads release plan for each task
    if not file_path:
        raise ValueError("releases_file path is empty.")
    releases = []
    with open(file_path, newline="", encoding="utf-8") as f:
        tmp = csv.DictReader(f)
        for line in tmp:
            start = datetime.fromisoformat((line.get("start_date") or "").strip())
            end = datetime.fromisoformat((line.get("end_date") or "").strip())
            working_days = int((line.get("working_days") or "").strip())
            if not start or not end or not working_days:
                continue
            releases.append(Release( start_day=start, end_date=end, working_days=working_days))
    return releases

def load_programmers_specs_from_file(file_path: str) -> List[Tuple[str, float]]:
    # loads name and efficiency per programmer
    if not file_path:
        raise ValueError("programmers_file path is empty.")
    prog = []
    with open(file_path, newline="", encoding="utf-8") as f:
        tmp = csv.DictReader(f)
        for line in tmp:
            name = (line.get("name") or "").strip()
            if not name:
                continue
            efficiency = float((line.get("efficiency") or "1.0").strip())
            prog.append((name, efficiency))
    return prog

tasks = load_tasks_from_file("data/ASF Jira 2025-12-08T08_13_21+0000.csv")
programmers = load_programmers_specs_from_file("data/sample_programmers.csv")
releases = load_releases_from_file("data/sample_releases.csv")


#TODO: remove debug prints
print("Loaded tasks:", len(tasks))
total_cost = sum(t.cost for t in tasks)
print("Total cost:", total_cost)
print("First task:", tasks[0])


print("Loaded programmers:", len(programmers))
print("First programmer:", programmers[0])


print("Loaded releases:", len(releases))
print("First release:", releases[0])

