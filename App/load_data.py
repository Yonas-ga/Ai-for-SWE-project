from typing import List, Tuple

from App.task import Task
from App.release import Release

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
            issue_id = (line.get("Issue id") or "").strip()
            priority = priority_map.get(line.get("Priority", ""), 4)
            time_spent = float((line.get("Time Spent") or "").strip())
            minutes_spent = time_spent // 60
            parent_id = (line.get("Parent id") or "").strip()
            parent_key = (line.get("Inward issue link (Child-Issue)") or "").strip()
            rows.append((issue_key, minutes_spent, priority, issue_id, parent_id, parent_key))
    tasks = []
    key_to_index = {}
    id_to_index = {}
    for i in range(len(rows)):  
        tasks.append(Task(id=i, name=rows[i][0], cost=rows[i][1], priority=rows[i][2], dependencies=[]))
        key_to_index[rows[i][0]] = i
        if rows[i][3] != "":
            id_to_index[rows[i][3]] = i
    for i in range(len(rows)):
        dep_indices = set()
        
        parent_id = rows[i][4]
        if parent_id != "" and parent_id in id_to_index:
            dep_indices.add(id_to_index[parent_id])
        
        parent_key = rows[i][5]
        if parent_key and parent_key in key_to_index:
            dep_indices.add(key_to_index[parent_key])
        
        for dep_index in dep_indices:
            tasks[i].dependencies.append(tasks[dep_index])   
    return sorted(tasks, key=lambda t: t.id)


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
            releases.append(Release(start_day=start, end_date=end, working_days=working_days))
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


# TODO: remove debug prints
if __name__ == "__main__":
    tasks = load_tasks_from_file("data/ASF Jira 2025-12-08T08_13_21+0000.csv")
    programmers = load_programmers_specs_from_file("data/sample_programmers.csv")
    releases = load_releases_from_file("data/sample_releases.csv")

    print("Loaded tasks:", len(tasks))
    total_cost = sum(t.cost for t in tasks)
    print("Total cost:", total_cost)
    print("First task:", tasks)

    print("Loaded programmers:", len(programmers))
    print("First programmer:", programmers[0])

    print("Loaded releases:", len(releases))
    print("First release:", releases[0])
