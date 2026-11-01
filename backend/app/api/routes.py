import os
import secrets
import sqlite3
from io import BytesIO

from fastapi import APIRouter, Cookie, File, Form, Header, HTTPException, Query, Response, UploadFile
from PIL import Image, UnidentifiedImageError

from ..schemas import (
    AnalysisResponse,
    ImageQualityAssessment,
    RecommendationRequest,
    RecommendationResponse,
)
from ..auth_schemas import LoginRequest, RegisterRequest, UserResponse
from ..services.auth import (
    SESSION_COOKIE,
    authenticate_user,
    create_session,
    create_user,
    get_user_for_session,
    normalize_email,
    revoke_session,
)
from ..services.quality_gate import assess_images
from ..services.predictor import PRODUCTS, filter_catalogue, match_products, simulate_analysis
from ..config import cookie_samesite, cookie_secure

router = APIRouter(prefix="/api")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024
MIN_DIMENSION = 128
MAGIC = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),
}


def _set_session_cookie(response: Response, token: str, expires_at) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite=cookie_samesite(),
        expires=expires_at,
        max_age=14 * 24 * 60 * 60,
    )


def _set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        "aerm_csrf",
        token,
        httponly=False,
        secure=cookie_secure(),
        samesite=cookie_samesite(),
        max_age=14 * 24 * 60 * 60,
    )


def _require_csrf(
    csrf_cookie: str | None,
    csrf_header: str | None,
) -> None:
    if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(status_code=403, detail="CSRF validation failed.")


@router.get("/auth/csrf")
def csrf(response: Response) -> dict[str, str]:
    token = secrets.token_urlsafe(32)
    _set_csrf_cookie(response, token)
    return {"csrf_token": token}


@router.post("/auth/register", response_model=UserResponse, status_code=201)
def register(
    request: RegisterRequest,
    response: Response,
    aerm_csrf: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
) -> UserResponse:
    _require_csrf(aerm_csrf, x_csrf_token)
    try:
        user = create_user(request.name, normalize_email(str(request.email)), request.password)
    except sqlite3.IntegrityError as exc:
        if "UNIQUE constraint failed" in str(exc):
            raise HTTPException(status_code=409, detail="An account with that email already exists.") from exc
        raise
    token, expires_at = create_session(user["id"])
    _set_session_cookie(response, token, expires_at)
    _set_csrf_cookie(response, secrets.token_urlsafe(32))
    return UserResponse(**user)


@router.post("/auth/login", response_model=UserResponse)
def login(
    request: LoginRequest,
    response: Response,
    aerm_csrf: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
) -> UserResponse:
    _require_csrf(aerm_csrf, x_csrf_token)
    user = authenticate_user(str(request.email), request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    token, expires_at = create_session(user["id"])
    _set_session_cookie(response, token, expires_at)
    _set_csrf_cookie(response, secrets.token_urlsafe(32))
    return UserResponse(**user)


@router.post("/auth/logout", status_code=204)
def logout(
    response: Response,
    aerm_session: str | None = Cookie(default=None),
    aerm_csrf: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
) -> Response:
    _require_csrf(aerm_csrf, x_csrf_token)
    revoke_session(aerm_session)
    response.delete_cookie(SESSION_COOKIE)
    response.delete_cookie("aerm_csrf")
    response.status_code = 204
    return response


@router.get("/auth/me", response_model=UserResponse)
def current_user(aerm_session: str | None = Cookie(default=None)) -> UserResponse:
    user = get_user_for_session(aerm_session)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return UserResponse(**user)


@router.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "aerm-ai-api",
        "demo_mode": True,
        "model": "phase1-deterministic-skin-simulator",
        "image_quality_gate_configured": bool(os.getenv("AERM_QUALITY_MODEL_PATH")),
    }


async def read_image(image: UploadFile, slot: str) -> tuple[str, bytes]:
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"{slot} must be a JPG, PNG, or WEBP image.")
    content = await image.read()
    if not content:
        raise HTTPException(status_code=422, detail=f"{slot} is empty.")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"{slot} must be smaller than 10 MB.")
    if not any(content.startswith(signature) for signature in MAGIC[image.content_type]):
        raise HTTPException(status_code=422, detail=f"{slot} does not contain a valid image payload.")
    try:
        with Image.open(BytesIO(content)) as decoded:
            decoded.verify()
        with Image.open(BytesIO(content)) as decoded:
            width, height = decoded.size
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=422, detail=f"{slot} could not be decoded as an image.")
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise HTTPException(status_code=422, detail=f"{slot} must be at least {MIN_DIMENSION}x{MIN_DIMENSION} pixels.")
    return image.filename or slot, content


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    front: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    budget_inr: int | None = Form(default=None, ge=0),
    fragrance_free: bool = Form(default=False),
) -> AnalysisResponse:
    images = [await read_image(front, "Front image"), await read_image(left, "Left image"), await read_image(right, "Right image")]
    response = simulate_analysis(images, budget_inr=budget_inr, fragrance_free=fragrance_free)
    try:
        quality = assess_images(
            [(slot, content) for slot, (_name, content) in zip(("front", "left", "right"), images)]
        )
        response.image_quality = (
            ImageQualityAssessment.model_validate(quality) if quality else None
        )
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return response


@router.get("/products")
def products(category: str | None = Query(default=None), brand: str | None = Query(default=None),
             max_budget: int | None = Query(default=None, ge=0), ingredient: str | None = Query(default=None),
             fragrance_free: bool = False, sort: str = "match") -> list:
    return filter_catalogue(category, brand, max_budget, ingredient, fragrance_free, sort)


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(request: RecommendationRequest) -> RecommendationResponse:
    products, routine, ingredients, explanations = match_products(
        request.concerns,
        budget_inr=request.budget_inr,
        fragrance_free=request.fragrance_free,
        preferred_ingredients=request.preferred_ingredients,
    )
    return RecommendationResponse(
        products=products,
        routine=routine,
        matched_ingredients=ingredients,
        explanations=explanations,
    )
