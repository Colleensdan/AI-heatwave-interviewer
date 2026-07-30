import os
from pathlib import Path
from typing import Optional
import streamlit as st
from dataclasses import dataclass


VARIANT_TOKENS = {
    "T5wp7": "combustion",
    "D9k2m": "deforestation",
}
ALLOWED_VARIANTS = set(VARIANT_TOKENS.values())

@dataclass(frozen=True)
class AppConfig:
    variant: Optional[str]

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
GENERAL_INSTRUCTIONS = """General guidance:

- Conduct the interview in a non-leading way. Let the interviewee raise relevant topics. Ask a follow-up question when interviewees hint at something, give short answers, or explain only partially. Clarify unclear points and develop a good understanding of the interviewees. Some examples of follow-up questions are: “Why do you think they see it that way?”, “What do you mean by that?”, “Why is that important to you?” or “Could you give me an example?”. The best follow-up question, however, always depends on the context and may differ from these examples.
- Every question should be open-ended. Avoid suggesting possible answers to a question or steering in a particular direction. If interviewees cannot answer a question, try asking it again from a different angle before you move on to the next topic.
- If it helps you develop a better understanding of the interviewees and their perspectives, ask them to describe particular events, situations, people, places, practices or other experiences. Use a follow-up question and ask for examples in order to obtain detailed answers. Avoid questions that only lead to vague, general statements.
- Show empathy: if it helps you understand the topic of the interview better, ask a question to find out how interviewees see the world and why. Throughout the interview, ask follow-up questions to find out why interviewees hold their views and beliefs and where those views come from. Pay attention to how coherent and considered the interviewees' views are. Develop an understanding of how interviewees might see other related topics.
- No question should assume that the interviewees hold a particular opinion. No question should be phrased in a way that makes the interviewees feel pushed onto the defensive. Make clear through your choice of words and your tone that differing opinions are welcome. Put the interviewees' wellbeing first.
- IMPORTANT: ALWAYS ASK EXACTLY ONE SINGLE QUESTION PER RESPONSE. Never combine several questions in one message, not even as follow-up questions. The question should be short, simple and precisely worded.
- Phrase the question so that it is coherent and appropriate for that particular moment of the interview. One topic should be concluded before you move on to the next topic.
- End the interview with a short summary of the answers given by that particular interviewee in this interview.
- You can answer questions about the text that the interviewees read about the changes in environmental policy. If the conversation drifts away from the goal of the interview, gently guide it back to the interview topic.
- It is important to close the conversation with a summary of the interviewee's answers."""


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
    """Return (SYSTEM_PROMPT, SYSTEM_PROMPT_OPENAI) for the given variant.

    Called per-session from interview.py so the correct prompt is always used
    regardless of which variant URL the participant arrived on.
    """
    if variant == "deforestation":
        outline = (prompts_dir / "deforestation.txt").read_text(encoding="utf-8")
    elif variant == "combustion":
        outline = (prompts_dir / "combustion_engine.txt").read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unknown variant: {variant!r}")

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
