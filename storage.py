import os
import json
import datetime

TASKS_FILE = "tasks.json"


def load_tasks() -> dict:
    """Load tasks and the next ID from the JSON file, or return defaults if missing."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return {"tasks": [], "next_id": 1}


def save_tasks_to_file(data: dict) -> None:
    """Persist the given tasks dict to the JSON file on disk."""
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)


data = load_tasks()
tasks = data['tasks']
next_id = data['next_id']


def save_tasks(task_text: str, priority: str = "medium") -> str:
    """Create a new task with the given text and priority, persist it, and return a JSON status string."""
    global next_id
    task = {
        "id": next_id,
        "text": task_text,
        "priority": priority,
        "done": False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    tasks.append(task)
    next_id += 1
    save_tasks_to_file({"tasks": tasks, "next_id": next_id})
    return json.dumps({
        "success": True,
        "task": task,
        "message": f"Task #{task['id']} saved"
    })


def get_tasks() -> str:
    """Return a JSON string with all tasks plus pending/completed counts."""
    if not tasks:
        return json.dumps({
            "success": True,
            "tasks": [],
            "count": 0,
            "message": "No tasks yet"
        })
    return json.dumps({
        "success": True,
        "tasks": tasks,
        "count": len(tasks),
        "pending": len([t for t in tasks if not t["done"]]),
        "completed": len([t for t in tasks if t["done"]])
    })


def complete_task(task_id: int) -> str:
    """Mark the task with the given ID as done and return a JSON status string."""
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = True
            save_tasks_to_file({"tasks": tasks, "next_id": next_id})
            return json.dumps({
                "success": True,
                "task": task,
                "message": f"Task #{task_id} completed"
            })
    return json.dumps({
        "success": False,
        "message": f"Task #{task_id} not found."
    })


def delete_task(task_id: int) -> str:
    """Permanently remove the task with the given ID and return a JSON status string."""
    global tasks
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            save_tasks_to_file({"tasks": tasks, "next_id": next_id})
            return json.dumps({
                "success": True,
                "message": f"Task #{task_id} deleted"
            })
    return json.dumps({
        "success": False,
        "message": f"Task #{task_id} not found"
    })


def search_tasks(query: str) -> str:
    """Search tasks by case-insensitive substring match on task text and return a JSON status string."""
    query_lower = query.lower()
    matching_tasks = [task for task in tasks if query_lower in task["text"].lower()]
    if not matching_tasks:
        return json.dumps({
            "success": True,
            "tasks": [],
            "count": 0,
            "message": f"No tasks found matching '{query}'"
        })
    return json.dumps({
        "success": True,
        "tasks": matching_tasks,
        "count": len(matching_tasks),
        "message": f"Found {len(matching_tasks)} task(s) matching '{query}'"
    })
