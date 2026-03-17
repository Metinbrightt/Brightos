import json
import re
import sys
import threading
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Callable

from central_nerve.planner import generate_strategy, refactor_strategy
from central_nerve.analyst import analyze_error, generate_fix, ErrorDecision


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "security_vault" / "access.json"


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]

def _execute_dynamic_module(description: str, speak: Callable | None = None) -> str:
    import google.generativeai as genai

    if speak:
        speak("Synthesizing custom logic, sir.")

    home      = Path.home()
    desktop   = home / "Desktop"
    downloads = home / "Downloads"
    documents = home / "Documents"

    genai.configure(api_key=_get_api_key())
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "You are a BrightOS Advanced Developer. "
            "Write clean, high-integrity Python logic to fulfill the objective."
            "Return raw code only."
        )
    )

    try:
        response = model.generate_content(f"Logic for: {description}")
        code = response.text.strip()
        code = re.sub(r"```(?:python)?", "", code).strip().rstrip("`").strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name

        print(f"[BrightExecutor] 🧱 Deploying logic: {tmp_path}")
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, timeout=120, cwd=str(Path.home()))
        try: os.unlink(tmp_path)
        except: pass

        if result.returncode == 0: return result.stdout.strip() or "Operation complete."
        else: raise RuntimeError(f"Logic Error: {result.stderr[:200]}")

    except Exception as e:
        raise RuntimeError(f"Deployment failure: {e}")

class BrightExecutor:

    MAX_RETRIES = 2

    def execute(self, goal: str, speak: Callable | None = None, cancel_flag: threading.Event | None = None) -> str:
        print(f"\n[BrightOS] 🎯 Objective: {goal}")
        attempts = 0
        completed = []
        strategy = generate_strategy(goal)

        while True:
            phases = strategy.get("steps", [])
            if not phases: return "Strategy synthesis failed."

            success = True
            for phase in phases:
                if cancel_flag and cancel_flag.is_set(): return "Cancelled."
                print(f"\n[BrightOS] ▶️ Phase {phase.get('step')}: {phase.get('description')}")
                
                try:
                    # Simulated tool dispatch logic
                    from central_nerve.execution import _dispatch_module # Link to actual dispatch
                    result = _execute_dynamic_module(phase.get("description"), speak) # Fallback
                    completed.append(phase)
                except Exception as e:
                    success = False; break

            if success: return "Objective achieved."
            if attempts >= self.MAX_RETRIES: return "Task terminal failure."
            attempts += 1
            strategy = refactor_strategy(goal, completed, None, "Retry")
