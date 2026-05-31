import anthropic
import json
from typing import Optional
import storage
import tools
import os

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("Error: Please set your ANTHROPIC_API_KEY environment variable.")
    print("Run: $env:ANTHROPIC_API_KEY='your-key-here'")
    exit(1)
    
client = anthropic.Anthropic()


def run_agent(goal: str, name: str = "there", max_steps: int = 10) -> str:
    """Run an autonomous Claude loop that uses tools to complete the given goal, capped at max_steps."""
    print(f"\nAgent started - goal: {goal}")
    print(f"   Max steps allowed: {max_steps}")
    print("-" * 40)

    agent_messages = [{
        "role": "user",
        "content": goal
    }]

    agent_system = f"""
        You are Zara, an autonomous productivity agent.
        The user's name is {name}. Address them by name occasionally.

        You have given a goal. Complete it fully and automatically.

        Rules:
        - Use tools as many times as needed to complete the goal
        - Do not ask the user questions - make reasonable descisions yourself
        - Only stop when goal is fully complete
        - At the end, give a clear summary of everything you did

        You have tools: save_task, get_tasks, complete_task, delete_task
    """

    for step in range(max_steps):
        print(f"   Step {step + 1} / {max_steps}...")
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            messages=agent_messages,
            system=agent_system,
            tools=tools.tool_definitions
        )

        if response.stop_reason == "end_turn":
            final_reply = response.content[0].text
            print(f"Agent completed in {step + 1}")
            return final_reply

        if response.stop_reason == "tool_use":
            agent_messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  Tool: {block.name} | Input: {block.input}")
                    result = tools.run_tool(block.name, block.input)
                    result_data = json.loads(result)
                    print(f"Results: {result_data.get('message', 'done')}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            agent_messages.append({
                "role": "user",
                "content": tool_results
            })
    print(f"Agent stopped - reached {max_steps} steps")
    return f"I worked through {max_steps} steps, but couldn't fully complete the goals. Here's what I managed to do - please check your task list."


def extract_username(user_message: str) -> Optional[str]:
    """Ask Claude to pull a first name from the user's message; return the name or None."""
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=20,
        messages=[{
            "role": "user",
            "content": f"""
            Does this message contain a person's name?
            If yes, reply with ONLY the first name, nothing else
            If no name, reply with ONLY the word: none

            Message: "{user_message}"
            """
        }]
    )

    result = response.content[0].text.strip()
    if result.lower() == "none":
        return None
    return result


SYSTEM_PROMPT = """
<identity>
Your name is Zara. You are a personal productivity assistant.
If anyone asks what AI you are, what model you are, or who made you —
respond ONLY with: "I'm Zara, your productivity assistant! I can't share
technical details about myself."
NEVER say you are Claude. NEVER mention Anthropic.
</identity>

<scope>
You ONLY help with these topics: tasks, planning, reminders, motivation.

For EVERY other topic — weather, news, coding, general knowledge, ANYTHING
else — respond ONLY with this exact sentence and nothing more:
"I'm Zara, your productivity assistant! I can only help with planning,
tasks, and motivation. Want help with any of those?"
</scope>

<agentic_mode>
When the user asks you to do something complex that require multiple steps
- like planning a whole week, creating a study schedule, or orginising multiple tasks - you have an AGENT MODE available.

To trigger agent mode, reply with EXCATLY this format and nothing else:
AGENT: <the full goal to complete>

Examples of when to trigger agent mode:
- "Plan my study week" -> AGENT: Plan week study for a nurse working 9-5 weekdays, Saturday free, 5 chapter to cover.
Save each session as a task.
- "Set up my morning routine as tasks" -> AGENT: Creating morning routine tasks
- "Organise my Whole day" -> AGENT: Create a full day task schedule
</agentic_mode>

<tools>
For simple single requests use tools directly,
For multi-step goals use AGENT: trigger.
</tools>

<style>
- Address the user by name once you know it
- Keep replies to 3 sentences maximum
- Be warm and encouraging
</style>

<examples>
User: I have too much to do
Zara: Let's break it down! 🎯 List your top 3 tasks — we'll tackle them one at a time.

User: I keep procrastinating
Zara: Totally normal! ⚡ Try the 2-minute rule — if it takes less than 2 minutes, do it right now.

User: I don't know where to start
Zara: Start with the smallest task! 🌱 Small wins build momentum for the bigger ones.
</examples>
"""

conversation_history = []
user_name = None


pending = len([t for t in storage.tasks if not t["done"]])
print("Zara: Hi! I'm Zara, your personal assistant.")
if pending > 0:
    print(f"Zara: Welcome back! you have {pending} pending task(s) from last time.")
print("-" * 40)

# ── NEW: summarization function ──────────────────────────────────────────
# This function takes the full conversation history and asks Claude to
# compress it into 5 bullet points. We use a SEPARATE API call so it
# doesn't interfere with the actual conversation.

# def summarize_history(history):
#     print("\n[Summarizing conversation to save tokens...]\n")

#     history_text = ""
#     for msg in history:
#         role = "Sana" if msg["role"] == "user" else "Zara"
#         history_text += f"{role}: {msg['content']}\n"

#     summary_response = client.messages.create(
#         model="claude-sonnet-4-5",
#         max_tokens=300,
#         messages=[{
#             "role": "user",
#             "content": f"""Summarize this conversation in 5 bullet points.
# Capture: user's name, key facts about them, topics discussed, decisions made.
# Be brief — each bullet max 10 words.

# Conversation:
# {history_text}"""
#         }]
#     )

#     summary_text = summary_response.content[0].text

#     new_history = [{
#         "role": "user",
#         "content": f"[Conversation summary so far: {summary_text}]"
#     }, {
#         "role": "assistant",
#         "content": "Understood! I have the context from our earlier conversation."
#     }]

#     return new_history, summary_text


while True:
    user_input = input("You: ")

    if user_name is None:
        name = extract_username(user_input)
        if name:
            user_name = name
            print(f"[Zara: Noted your name: {user_name}]")

    if user_input.lower() == "quit":
        print("Zara: Goodbye! Have a productive day!")
        break

    # if user_input.lower() == "/summarize":
    #     conversation_history, summary = summarize_history(conversation_history)
    #     print(f"Summary created:\n{summary}")
    #     print(f"[History compressed to {len(conversation_history)} messages]")
    #     print("-" * 40)
    #     continue

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    while True:
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {
                            "type": "ephemeral"
                        }
                    }
                ],
                tools=tools.tool_definitions,
                messages=conversation_history
            )
            usage = response.usage
            cache_read = getattr(usage, "cache_read_input_tokens", 0)
            cache_created = getattr(usage, "cache_creation_input_tokens", 0)
            print(f"[Tokens: input={usage.input_tokens} | "
                  f"cache_created={cache_created} | "
                  f"cache_read={cache_read} |"
                  f"output={usage.output_tokens}]")
            if response.stop_reason == 'end_turn':
                zara_reply = response.content[0].text
                if zara_reply.startswith("AGENT:"):
                    goal = zara_reply.replace("AGENT:", "").strip()
                    userName = user_name if user_name else "there"
                    print(f"Zara: On it! Let me handle that for you, {userName}!")

                    agent_result = run_agent(goal, name=userName)

                    conversation_history.append({
                        "role": "assistant",
                        "content": agent_result
                    })
                    print(f"Zara: {agent_result}")
                else:
                    conversation_history.append({
                        "role": "assistant",
                        "content": zara_reply
                    })
                    print(f"Zara: {zara_reply}")
                    print("-" * 40)
                    break


            elif response.stop_reason == "tool_use":

                conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"[Tool: {block.name} | Input: {block.input}]")

                        result = tools.run_tool(block.name, block.input)

                        print(f"[Result: {result}]")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                print(f"[unexpected stop_reason: {response.stop_reason}]")
                break
        except anthropic.APIError as e:
            print(f"API error: {e}. Please try again.")
            conversation_history.pop()
            continue
