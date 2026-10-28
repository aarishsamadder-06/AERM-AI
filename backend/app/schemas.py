from typing import Literal

from pydantic import BaseModel, Field


Concern = Literal["acne", "dryness", "redness", "texture", "dark_spots", "sensitivity"]


class SkinFinding(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    severity: Literal["low", "medium", "high"]
    summary: str


class Product(BaseModel):
    id: str
    name: str
    category: Literal["cleanser", "moisturizer", "sunscreen", "serum"]
    brand: str
    price_inr: int = Field(gt=0)
    ingredients: list[str]
    concerns: list[Concern]
    why: str
    match_explanation: str = ""
    usage: str
    sample_data: bool
    source: str
    image_url: str | None = None
    image_placeholder: str = "Product image unavailable"
    fragrance_free: bool
    availability: Literal["in_stock", "limited", "unavailable"]


class RoutineStep(BaseModel):
    time: Literal["morning", "evening", "weekly"]
    step: str
    action: str
    rationale: str


class AnalysisResponse(BaseModel):
    finding: SkinFinding
    views: list[str]
    detected_concerns: list[Concern]
    matched_ingredients: list[str]
    rationale: list[str]
    routine: list[RoutineStep]
    observations: list[str]
    recommendations: list[str]
    products: list[Product]
    simulation_notice: str


class RecommendationRequest(BaseModel):
    concerns: list[Concern] = Field(default_factory=list)
    budget_inr: int | None = Field(default=None, ge=0)
    fragrance_free: bool = False
    preferred_ingredients: list[str] = Field(default_factory=list)
    category: str | None = None
    brand: str | None = None
    sort: Literal["match", "price_asc", "price_desc", "name"] = "match"


class RecommendationResponse(BaseModel):
    products: list[Product]
    routine: list[RoutineStep]
    matched_ingredients: list[str]
    explanations: list[str]
