from .ai_service import GeminiService
from .config import get_settings


def generate_nutrition_tip_with_flash(*, goal: str, age: int, weight: float) -> str:
    settings = get_settings()
    service = GeminiService()

    prompt = f"""
Give one concise nutrition or recovery tip for a FitBuddy user.

Goal: {goal}
Age: {age}
Weight: {weight} kg

Requirements:
- 3–6 sentences maximum.
- Practical general-wellness guidance.
- Do not prescribe a specific calorie target or medical diet.
- Use hydration, balanced meals, protein/fiber, or recovery when relevant.
- Do not diagnose or treat disease.
""".strip()

    return service.generate(
        model=settings.gemini_tip_model,
        prompt=prompt,
        max_output_tokens=500,
    )
