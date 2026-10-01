from .ai_service import GeminiService
from .config import get_settings


def generate_workout_gemini(*, name: str, age: int, weight: float, goal: str, intensity: str) -> str:
    settings = get_settings()
    service = GeminiService()

    prompt = f"""
You are FitBuddy, a careful fitness-planning assistant.

Create a personalized 7-day workout plan for:
- Name: {name}
- Age: {age}
- Weight: {weight} kg
- Fitness goal: {goal}
- Preferred intensity: {intensity}

Return plain text only with:
1. Safety note
2. Weekly overview
3. Day 1 through Day 7

For every day include:
- Focus
- Warm-up (5–10 minutes)
- Main workout with exercise names and sets/reps or duration
- Rest guidance
- Cool-down/recovery

Adapt difficulty to the requested intensity and include at least one recovery/rest-oriented day.
Do not diagnose medical conditions, prescribe treatment, or promise specific results.
If the user appears to need professional medical advice, say so clearly.
""".strip()

    return service.generate(
        model=settings.gemini_workout_model,
        prompt=prompt,
        max_output_tokens=6000,
    )
