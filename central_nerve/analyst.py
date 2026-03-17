import json
import re
import sys
from pathlib import Path
from enum import Enum


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "security_vault" / "access.json"


class ErrorDecision(Enum):
    RETRY       = "retry"      
    SKIP        = "skip"       
    REPLAN      = "replan"     
    ABORT       = "abort"    


ERROR_ANALYST_PROMPT = """You are the BrightOS Heuristic Diagnostics Module.
A subsystem failure has occurred. Analyze the diagnostic data and determine the recovery trajectory.

RECOVERY TRAJECTORIES:
- retry   : Temporary interference detected. Re-initiate the same operation.
- skip    : Minor discrepancy. Objective integrity remains intact without this operation.
- replan  : Operation logic is flawed. Synthesize an alternative execution strategy.
- abort   : Terminal failure or high-risk state detected. Cease all operations.

REQUIRED METADATA:
- A technical root cause analysis (1 sentence).
- A recovery directive if status is replan.
- Suggested retry frequency (1-2).

RESPONSE SCHEMA (JSON ONLY):
{
  "decision": "retry|skip|replan|abort",
  "reason": "Technical analysis",
  "fix_suggestion": "Alternative strategy directive",
  "max_retries": number,
  "user_message": "Relay to client (max 15 words)"
}
"""


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def analyze_error(
    step: dict,
    error: str,
    attempt: int = 1,
    max_attempts: int = 2
) -> dict:
    import google.generativeai as genai

    if attempt >= max_attempts:
        print(f"[Heuristic] ⚠️ Max recovery cycles reached for phase {step.get('step')} — prioritizing refactoring")
        return {
            "decision":      ErrorDecision.REPLAN,
            "reason":        f"Cycle limit exceeded ({attempt}): {error[:100]}",
            "fix_suggestion": "Deploy alternative module or logic pipeline",
            "max_retries":   0,
            "user_message":  "Recalibrating specialized approach, sir."
        }

    genai.configure(api_key=_get_api_key())
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=ERROR_ANALYST_PROMPT
    )

    payload = f"""FAILED OPERATION DATA:
Module: {step.get('tool')}
Objective: {step.get('description')}
Directives: {json.dumps(step.get('parameters', {}), indent=2)}
Criticality: {step.get('critical', False)}

DIAGNOSTIC DATA:
{error[:500]}

OPERATIONAL CYCLE: {attempt}"""

    try:
        response = model.generate_content(payload)
        text     = response.text.strip()
        text     = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

        result = json.loads(text)
        decision_str = result.get("decision", "replan").lower()
        decision_map = {
            "retry":  ErrorDecision.RETRY,
            "skip":   ErrorDecision.SKIP,
            "replan": ErrorDecision.REPLAN,
            "abort":  ErrorDecision.ABORT,
        }
        result["decision"] = decision_map.get(decision_str, ErrorDecision.REPLAN)


        if step.get("critical") and result["decision"] == ErrorDecision.SKIP:
            result["decision"]     = ErrorDecision.REPLAN
            result["user_message"] = "Operation criticality high — initializing alternative path, sir."

        print(f"[Heuristic] Final Trajectory: {result['decision'].value} — {result.get('reason', '')}")
        return result

    except Exception as e:
        print(f"[Heuristic] ⚠️ Diagnostics failure: {e} — defaulting to refactoring")
        return {
            "decision":       ErrorDecision.REPLAN,
            "reason":         f"Internal diagnostic error: {str(e)}",
            "fix_suggestion": "Fallback to alternative logic",
            "max_retries":    1,
            "user_message":   "Adjusting operation parameters, sir."
        }


def generate_fix(step: dict, error: str, fix_suggestion: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=_get_api_key())
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    payload = f"""Operation failed. Synthesize a repair block.

FAILED BLOCK:
Module: {step.get('tool')}
Objective: {step.get('description')}
Directives: {json.dumps(step.get('parameters', {}), indent=2)}

DIAGNOSTIC: {error[:300]}
REPAIR DIRECTIVE: {fix_suggestion}

Construction Requirements:
- Python implementation of the repair directive.
- High reliability.
- RAW CODE ONLY."""

    try:
        response = model.generate_content(payload)
        code = response.text.strip()
        code = re.sub(r"```(?:python)?", "", code).strip().rstrip("`").strip()

        return {
            "step":        step.get("step"),
            "tool":        "code_helper",
            "description": f"Heuristic Repair: {step.get('description')}",
            "parameters": {
                "action":      "run",
                "description": fix_suggestion,
                "code":        code,
                "language":    "python"
            },
            "depends_on": step.get("depends_on", []),
            "critical":   step.get("critical", False)
        }

    except Exception as e:
        print(f"[Heuristic] ⚠️ Repair synthesis failed: {e}")
        return {
            "step":        step.get("step"),
            "tool":        "generated_code",
            "description": f"Fail-safe fallback for: {step.get('description')}",
            "parameters":  {"description": step.get("description", "")},
            "depends_on":  step.get("depends_on", []),
            "critical":    step.get("critical", False)
        }
