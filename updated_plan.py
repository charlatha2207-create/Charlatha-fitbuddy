from .ai_service import GeminiService
from .config import get_settings


def update_workout_plan(*, original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    settings = get_settings()
    service = GeminiService()

    prompt = f"""
You are revising a FitBuddy 7-day workout plan.

Fitness goal: {goal}
Preferred intensity: {intensity}

Original plan:
---BEGIN ORIGINAL PLAN---
{original_plan}
---END ORIGINAL PLAN---

User feedback:
---BEGIN FEEDBACK---
{feedback}
---END FEEDBACK---

Create a revised 7-day plan that preserves useful parts of the original while addressing the feedback.
Return plain text with:
1. Revision summary
2. Day 1 through Day 7
3. Safety/recovery note

Do not diagnose, prescribe treatment, or promise outcomes.
If feedback requests something unsafe or medically inappropriate, replace it with a safer general alternative.
""".strip()

    return service.generate(
        model=settings.gemini_workout_model,
        prompt=prompt,
        max_output_tokens=6000,
    )
