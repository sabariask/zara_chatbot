import json
import storage


tool_definitions = [
    {
        "name": "save_task",
        "description": "Saves a new task to the user's taks list. Use this whenever the user wants to add, save or remember a task, to-do item, or reminder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_text": {
                    "type": "string",
                    "description": "The task to save, e.g. 'buy textbook' or 'study chapter 3'"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Priority level. Use high for urgent/important tasks, low for someday tasks."
                }
            },
            "required": ["task_text"]
        }
    },
    {
        "name": "get_tasks",
        "description": "Shows all tasks in the user's task list. Use this when the user asks to see, list, show, or check their tasks.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "complete_task",
        "description": "Marks a task as complete or done. Use this when the user says they finished, completed, or did a task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID number of the task to mark complete"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Deletes a task permanently. use when user wants to remove or delete a task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "search_tasks",
        "description": "Searches the user's tasks for a keyword or phrase in the task text. Use this when the user wants to find, search, look up, or filter tasks by name or topic (e.g. 'find my study tasks', 'do I have anything about groceries?').",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The keyword or phrase to search for. Matched case-insensitively against each task's text."
                }
            },
            "required": ["query"]
        },
        "cache_control": {
            "type": "ephemeral"
        }
    }
]


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch a tool call from Claude to the matching local function and return its JSON result."""
    if tool_name == "save_task":
        return storage.save_tasks(**tool_input)
    elif tool_name == 'get_tasks':
        return storage.get_tasks()
    elif tool_name == 'complete_task':
        return storage.complete_task(**tool_input)
    elif tool_name == 'delete_task':
        return storage.delete_task(**tool_input)
    elif tool_name == 'search_tasks':
        return storage.search_tasks(**tool_input)
    else:
        return json.dumps({"success": False, "message": f"Unknown tool: {tool_name}"})
