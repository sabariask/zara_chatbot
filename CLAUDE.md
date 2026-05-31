# Zara Chatbot Project

## What this project is
A personal productivity chatbot built with the Anthropic Python SDK.
Zara is a persona — she only handles tasks, planning, and motivation.
The main file is chatbot.py. Tasks persist in tasks.json.

## Tech stack
- Language: Python 3
- SDK: anthropic (pip install anthropic)  
- Storage: tasks.json (auto-created JSON file)
- Model: claude-sonnet-4-5

## Coding standards
- Add a docstring to every function explaining what it does
- Use type hints on all function parameters and return values
- Keep functions short — one job per function
- Never hardcode the API key — always use ANTHROPIC_API_KEY env variable
- Return structured JSON from all tool functions (success, message fields)

## Project structure
chatbot.py        → main application
tasks.json        → task storage (never edit manually)
CLAUDE.md         → this file
.claude/commands/ → custom slash commands

## Important rules
- Never modify tasks.json directly — only via save_tasks_to_file()
- tool_definitions list must stay in sync with run_tool() dispatcher
- All tool functions must return JSON strings with success field
- Test changes by running: python chatbot.py
- The agent's max_steps must never be removed — it prevents infinite loops

## What NOT to do
- Do not add tools without updating both tool_definitions AND run_tool()
- Do not change the model name without checking deprecation status
- Do not remove the conversation_history list — it is the chat memory