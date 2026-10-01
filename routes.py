from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .ai_service import GeminiServiceError
from .database import get_db
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .models import Plan, User
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()
api_router = APIRouter(prefix="/api/v1", tags=["FitBuddy API"])


def render_error(request: Request, message: str, status_code: int = 400):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"message": message, "status_code": status_code},
        status_code=status_code,
    )


def get_user_and_plan(db: Session, user_id: str):
    user = db.scalar(select(User).where(User.user_id == user_id))
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id).order_by(Plan.id.desc()))
    return user, plan


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = UserInput(
            user_id=user_id, name=username, age=age, weight=weight,
            goal=goal, intensity=intensity
        )
    except ValidationError as exc:
        return render_error(request, str(exc), 422)

    try:
        workout_plan = generate_workout_gemini(
            name=payload.name, age=payload.age, weight=payload.weight,
            goal=payload.goal, intensity=payload.intensity
        )
        nutrition_tip = generate_nutrition_tip_with_flash(
            goal=payload.goal, age=payload.age, weight=payload.weight
        )
    except GeminiServiceError as exc:
        return render_error(request, str(exc), 503)

    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if user:
        user.name = payload.name
        user.age = payload.age
        user.weight = payload.weight
        user.goal = payload.goal
        user.intensity = payload.intensity
    else:
        user = User(**payload.model_dump())
        db.add(user)

    plan = Plan(
        user_id=payload.user_id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )
    db.add(plan)
    db.commit()
    db.refresh(user)
    db.refresh(plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"user": user, "plan": plan, "current_plan": workout_plan, "message": None},
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = FeedbackRequest(feedback=feedback)
    except ValidationError as exc:
        return render_error(request, str(exc), 422)

    user, plan = get_user_and_plan(db, user_id)
    if not user or not plan:
        return render_error(request, "User or workout plan was not found.", 404)

    try:
        revised = update_workout_plan(
            original_plan=plan.updated_plan or plan.original_plan,
            feedback=payload.feedback,
            goal=user.goal,
            intensity=user.intensity,
        )
    except GeminiServiceError as exc:
        return render_error(request, str(exc), 503)

    plan.updated_plan = revised
    plan.latest_feedback = payload.feedback
    db.commit()
    db.refresh(plan)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "current_plan": revised,
            "message": "Your plan was updated successfully using your feedback.",
        },
    )


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin_login.html", context={"error": None}
    )


@router.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    from .config import get_settings

    settings = get_settings()
    if username == settings.admin_username and password == settings.admin_password:
        request.session["is_admin"] = True
        return RedirectResponse("/view-all-users", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"error": "Invalid admin credentials."},
        status_code=401,
    )


@router.post("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


def admin_required(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse("/admin/login", status_code=303)
    return None


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    redirect = admin_required(request)
    if redirect:
        return redirect

    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    plans = db.scalars(select(Plan).order_by(Plan.id.desc())).all()
    plan_by_user = {}
    for plan in plans:
        plan_by_user.setdefault(plan.user_id, plan)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users, "plan_by_user": plan_by_user},
    )


@router.post("/admin/users/{user_id}/delete")
def delete_user(user_id: str, request: Request, db: Session = Depends(get_db)):
    redirect = admin_required(request)
    if redirect:
        return redirect

    user = db.scalar(select(User).where(User.user_id == user_id))
    if user:
        db.query(Plan).filter(Plan.user_id == user_id).delete()
        db.delete(user)
        db.commit()

    return RedirectResponse("/view-all-users", status_code=303)


@api_router.post("/plans")
def api_generate_plan(payload: UserInput, db: Session = Depends(get_db)):
    try:
        workout = generate_workout_gemini(
            name=payload.name, age=payload.age, weight=payload.weight,
            goal=payload.goal, intensity=payload.intensity
        )
        tip = generate_nutrition_tip_with_flash(
            goal=payload.goal, age=payload.age, weight=payload.weight
        )
    except GeminiServiceError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=503)

    user = db.scalar(select(User).where(User.user_id == payload.user_id))
    if user:
        user.name = payload.name
        user.age = payload.age
        user.weight = payload.weight
        user.goal = payload.goal
        user.intensity = payload.intensity
    else:
        user = User(**payload.model_dump())
        db.add(user)

    plan = Plan(user_id=payload.user_id, original_plan=workout, nutrition_tip=tip)
    db.add(plan)
    db.commit()

    return {
        "user_id": payload.user_id,
        "name": payload.name,
        "age": payload.age,
        "weight": payload.weight,
        "goal": payload.goal,
        "intensity": payload.intensity,
        "workout_plan": workout,
        "nutrition_tip": tip,
        "updated_plan": None,
    }


@api_router.get("/users/{user_id}")
def api_get_user(user_id: str, db: Session = Depends(get_db)):
    user, plan = get_user_and_plan(db, user_id)
    if not user or not plan:
        return JSONResponse({"detail": "User not found."}, status_code=404)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "age": user.age,
        "weight": user.weight,
        "goal": user.goal,
        "intensity": user.intensity,
        "workout_plan": plan.original_plan,
        "nutrition_tip": plan.nutrition_tip,
        "updated_plan": plan.updated_plan,
        "latest_feedback": plan.latest_feedback,
    }


@api_router.post("/plans/{user_id}/feedback")
def api_feedback(user_id: str, payload: FeedbackRequest, db: Session = Depends(get_db)):
    user, plan = get_user_and_plan(db, user_id)
    if not user or not plan:
        return JSONResponse({"detail": "User or plan not found."}, status_code=404)

    try:
        revised = update_workout_plan(
            original_plan=plan.updated_plan or plan.original_plan,
            feedback=payload.feedback,
            goal=user.goal,
            intensity=user.intensity,
        )
    except GeminiServiceError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=503)

    plan.updated_plan = revised
    plan.latest_feedback = payload.feedback
    db.commit()

    return {"user_id": user_id, "updated_plan": revised, "feedback": payload.feedback}


@api_router.get("/users")
def api_get_all_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        }
        for user in users
    ]
