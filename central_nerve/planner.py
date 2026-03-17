import json
import re
import sys
from pathlib import Path


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "security_vault" / "access.json"


PLANNER_PROMPT = """You are the core reasoning engine of BrightOS Neural Intelligence.
Your mission: Deconstruct user objectives into efficient execution pipelines using the available module suite.

FUNDAMENTAL PRINCIPLES:
- STRICTLY use the defined toolset. NO simulated scripts or unlisted functions.
- Every node in the pipeline must be self-contained; do not assume shared state between steps.
- Prefer web_search for real-time intelligence and data extraction.
- file_controller is your primary interface for data persistence.
- system_interface (cmd_control) handles binary execution and deep OS interaction.
- Maximum 5 nodes per pipeline. Efficiency is paramount.

MODULE SUITE & PARAMETERS:

open_app
  app_name: string (required)

web_search
  query: string (required) — focused, keyword-rich search string
  mode: "search" | "compare"
  items: list (optional)
  aspect: string (optional)

browser_control
  action: "go_to" | "search" | "click" | "type" | "scroll" | "get_text" | "press" | "close"
  url/query/text/direction: (context-appropriate)

file_controller
  action: "write" | "create_file" | "read" | "list" | "delete" | "move" | "copy" | "find"
  path: string (standard paths or absolute)
  name/content: (context-appropriate)

cmd_control
  task: string — objective description for system execution
  visible: boolean

computer_settings
  action/description/value: (system configuration parameters)

computer_control
  action: "type" | "click" | "hotkey" | "press" | "scroll" | "screenshot" | "screen_find"
  (coordinates or text as required)

screen_process
  text: analytical instruction for visual data processing

send_message
  receiver/message_text/platform: (communication directives)

reminder
  date/time/message: (temporal scheduling)

desktop_control
  action: "wallpaper" | "organize" | "clean" | "list" | "task"

youtube_video
  action: "play" | "summarize" | "trending"

weather_report
  city: string

code_helper
  action/description/language/file_path

dev_agent
  description/language

OBJECTIVE MAPPING EXAMPLES:

Client: "Research quantum computing and save a summary to my desktop."
Pipeline:
  1. web_search | query: "current state of quantum computing 2024 2025 technology summary"
  2. file_controller | action: write, path: desktop, name: quantum_research.txt, content: "[DATA RELATIVE TO SEARCH]"
  3. cmd_control | task: "open quantum_research.txt from desktop"

Client: "Message John on WhatsApp that I'm running late."
Pipeline:
  1. send_message | receiver: John, message_text: "I'm running late", platform: WhatsApp

OUTPUT SCHEMA — Provide valid JSON only:
{
  "goal": "string",
  "steps": [
    {
      "step": number,
      "tool": "string",
      "description": "string",
      "parameters": {},
      "critical": boolean
    }
  ]
}
"""


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def generate_strategy(goal: str, context: str = "") -> dict:
    import google.generativeai as genai

    genai.configure(api_key=_get_api_key())
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=PLANNER_PROMPT
    )

    input_payload = f"Objective: {goal}"
    if context:
        input_payload += f"\n\nContextual Data: {context}"

    try:
        response = model.generate_content(input_payload)
        text     = response.text.strip()
        text     = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

        strategy = json.loads(text)

        if "steps" not in strategy or not isinstance(strategy["steps"], list):
            raise ValueError("Invalid strategy structure")

        for step in strategy["steps"]:
            if step.get("tool") in ("generated_code",):
                print(f"[Strategy] ⚠️ Dynamic code injection detected — rerouting to web_search")
                desc = step.get("description", goal)
                step["tool"] = "web_search"
                step["parameters"] = {"query": desc[:200]}

        print(f"[Strategy] ✅ BrightOS Strategy: {len(strategy['steps'])} phases")
        for s in strategy["steps"]:
            print(f"  Phase {s['step']}: [{s['tool']}] {s['description']}")

        return strategy

    except json.JSONDecodeError as e:
        print(f"[Strategy] ⚠️ Interface parsing error: {e}")
        return _fallback_strategy(goal)
    except Exception as e:
        print(f"[Strategy] ⚠️ Engine failure: {e}")
        return _fallback_strategy(goal)


def _fallback_strategy(goal: str) -> dict:
    print("[Strategy] 🔄 Activating fail-safe routine")
    return {
        "goal": goal,
        "steps": [
            {
                "step": 1,
                "tool": "web_search",
                "description": f"Gathering data for: {goal}",
                "parameters": {"query": goal},
                "critical": True
            }
        ]
    }


def refactor_strategy(goal: str, completed_steps: list, failed_step: dict, error: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=_get_api_key())
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=PLANNER_PROMPT
    )

    history_summary = "\n".join(
        f"  - Phase {s['step']} ({s['tool']}): COMPLETED" for s in completed_steps
    )

    payload = f"""Objective: {goal}

Execution History:
{history_summary if history_summary else '  (initial phase)'}

Interruption in Phase: [{failed_step.get('tool')}] {failed_step.get('description')}
Diagnostic Error: {error}

Generate a REVISED execution strategy for the remaining objectives. Optimize and bypass the failure point."""

    try:
        response = model.generate_content(payload)
        text     = response.text.strip()
        text     = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
        strategy = json.loads(text)

        # code safety check
        for step in strategy.get("steps", []):
            if step.get("tool") == "generated_code":
                step["tool"] = "web_search"
                step["parameters"] = {"query": step.get("description", goal)[:200]}

        print(f"[Strategy] 🔄 Strategy refactored: {len(strategy['steps'])} phases remaining")
        return strategy
    except Exception as e:
        print(f"[Strategy] ⚠️ Refactoring failed: {e}")
        return _fallback_strategy(goal)
