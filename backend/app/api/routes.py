from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from PIL import Image, UnidentifiedImageError

from ..schemas import AnalysisResponse, RecommendationRequest, RecommendationResponse
from ..services.predictor import PRODUCTS, filter_catalogue, match_products, simulate_analysis

router = APIRouter(prefix="/api")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024
MIN_DIMENSION = 128
MAGIC = {
    "image/jpeg": (b"\xff\xd8\xff",),
    "image/png": (b"\x89PNG\r\n\x1a\n",),
    "image/webp": (b"RIFF",),
}


@router.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "service": "aerm-ai-api", "demo_mode": True, "model": "phase1-deterministic-skin-simulator"}


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
    return simulate_analysis(images, budget_inr=budget_inr, fragrance_free=fragrance_free)


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
