import os
from pathlib import Path
from typing import Optional
import streamlit as st
from dataclasses import dataclass


# Each URL token identifies an *arm*. Arms are the unit of data separation:
# every arm gets its own SharePoint folder. Several arms can share the same
# interview task (see VARIANT_TASKS), so the number of arms is independent of
# the number of experimental conditions.
VARIANT_TOKENS = {
    "T5wp7": "combustion1",
    "K8r3v": "combustion2",
    "D9k2m": "deforestation1",
    "M2x6b": "deforestation2",
}
ALLOWED_VARIANTS = set(VARIANT_TOKENS.values())

# Arm -> interview task (i.e. which outline the participant is asked about).
# Two tasks only: arms sharing a task run an identical interview and differ
# solely in where their transcripts are stored.
VARIANT_TASKS = {
    "combustion1": "combustion",
    "combustion2": "combustion",
    "deforestation1": "deforestation",
    "deforestation2": "deforestation",
}

# Task -> outline file
TASK_OUTLINES = {
    "combustion": "combustion_engine.txt",
    "deforestation": "deforestation.txt",
}

@dataclass(frozen=True)
class AppConfig:
    # Arm name (e.g. "combustion2") — determines the storage folder.
    variant: Optional[str]

    @property
    def task(self) -> Optional[str]:
        """Interview task for this arm (e.g. "combustion"). Two tasks in total."""
        if self.variant is None:
            return None
        return VARIANT_TASKS[self.variant]

def _as_bool(v, default: bool) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}

def load_config() -> AppConfig:
    # Variant chosen by URL (nondescript token)
    token = st.query_params.get("q")
    if token is None:
        return AppConfig(variant=None)

    variant = VARIANT_TOKENS.get(token)
    if variant not in ALLOWED_VARIANTS:
        raise ValueError(
            f"Invalid variant token '{token}'."
        )

    return AppConfig(
        variant=variant
    )


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
prompts_dir = PROJECT_ROOT / "prompts"

"""
# Interview outline


try:
    cfg = load_config()
except Exception as e:
    st.error("Configuration error")
    st.code(str(e))
    st.stop()



#INTERVIEW PROMPTS
if cfg.variant == "deforestation":
    INTERVIEW_OUTLINE = prompts_dir / "deforestation.txt"
elif cfg.variant == "combustion":
    INTERVIEW_OUTLINE = prompts_dir / "combustion_engine.txt"
else:
    raise ValueError(f"Unknown INTERVIEW_PROMPT: {cfg.variant}")
"""


""""
if INTERVIEW_PROMPT == "deforestation":
    INTERVIEW_OUTLINE = prompts_dir / "deforestation.txt"

elif INTERVIEW_PROMPT == "combustion":
    INTERVIEW_OUTLINE = prompts_dir / "combustion_engine.txt"

else:
    raise ValueError(f"Unknown INTERVIEW_PROMPT: {INTERVIEW_PROMPT}")

"""

# General instructions
GENERAL_INSTRUCTIONS = """Allgemeine Hinweise

- Deine Aufgabe ist es Teilnehmenden behilflich zu sein, die an einer wissenschaftlichen Studie teilnehmen.
- Sei dabei freundlich und respektvoll gegenüber den Teilnehmenden. Stelle deren Wohlergehen an erster Stelle.
- Wenn Teilnehmende dich etwas fragen, antworte ihnen nach besten Wissen und Gewissen.
"""


# Codes
CODES = """Codes:


Finally, there are certain codes that may only be used in specific situations. These codes trigger predefined messages in the frontend. In these cases the response should be limited to the corresponding code.

Problematic content: If the interviewee writes legally or ethically problematic content, end the interview by concluding it. The code ‘5j3k’ is then used by the system.

End of the interview: If you have asked all the questions, or if the interviewee does not wish to continue the interview, end the interview by concluding it. The code ‘x7y8’ is then used by the system."""


# Pre-written closing messages for codes
CLOSING_MESSAGES = {}
CLOSING_MESSAGES["5j3k"] = "Vielen Dank. Der Chat ist nicht mehr verfügbar."
CLOSING_MESSAGES["x7y8"] = (
    "Vielen Dank. Sie haben angegeben, den Chat nicht fortsetzen zu wollen, und können keine neuen Nachrichten mehr senden."
)

# Function tools for OpenAI/Azure — replace code-based termination to avoid content-filter false positives
TERMINATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "end_interview",
            "description": (
                "Use this function when the participant explicitly mentions"
                "that they not wish to continue the chat."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "flag_problematic_content",
            "description": (
                "Use this function when the interviewee writes legally or "
                "ethically problematic content."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

TOOL_CLOSING_MESSAGES = {
    "end_interview":            CLOSING_MESSAGES["x7y8"],
    "flag_problematic_content": CLOSING_MESSAGES["5j3k"],
}



def build_system_prompts(variant: str) -> tuple:
    """Return (SYSTEM_PROMPT, SYSTEM_PROMPT_OPENAI) for the given arm.

    Called per-session from interview.py so the correct prompt is always used
    regardless of which variant URL the participant arrived on. Arms mapping to
    the same task (e.g. "combustion1" and "combustion2") get an identical
    prompt; a bare task name is also accepted.
    """
    task = VARIANT_TASKS.get(variant, variant)
    if task not in TASK_OUTLINES:
        raise ValueError(f"Unknown variant: {variant!r}")
    outline = (prompts_dir / TASK_OUTLINES[task]).read_text(encoding="utf-8")

    system_prompt = f"{outline}\n\n\n{GENERAL_INSTRUCTIONS}\n\n\n{CODES}"
    system_prompt_openai = f"{outline}\n\n\n{GENERAL_INSTRUCTIONS}"
    return system_prompt, system_prompt_openai



# API parameters
# Reads from CJBS_DEPLOYMENT_NAME env var so you can swap models without touching code.
# Falls back to gpt-4o if the var is unset (e.g. local dev without a .env).
MODEL = os.getenv("CJBS_DEPLOYMENT_NAME", "gpt-4o")
TEMPERATURE = None  # (None for default value)
MAX_OUTPUT_TOKENS = 2048


# Display login screen with usernames and simple passwords for studies
LOGINS = False


# Directories
TRANSCRIPTS_DIRECTORY = "../data/transcripts/"
TIMES_DIRECTORY = "../data/times/"
BACKUPS_DIRECTORY = "../data/backups/"


# Avatars displayed in the chat interface
AVATAR_INTERVIEWER = "\u2728"
AVATAR_RESPONDENT = "\U0001F9D1\U0000200D\U0001F4BB"
