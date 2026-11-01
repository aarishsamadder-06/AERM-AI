import os
import pickle
import hashlib
import secrets
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError

try:
    from ml.quality_baseline import extract_features_from_bytes
except ModuleNotFoundError:
    from backend.ml.quality_baseline import extract_features_from_bytes

MODEL_ENV = "AERM_QUALITY_MODEL_PATH"
MODEL_NAME = "SCIN RBF SVM image-gradability model"
MODEL_DIGEST_ENV = "AERM_QUALITY_MODEL_SHA256"


@lru_cache(maxsize=1)
def _load_model(model_path: str):
    expected = os.getenv(MODEL_DIGEST_ENV, "").strip().lower()
    with Path(model_path).open("rb") as handle:
        contents = handle.read()
    if expected:
        actual = hashlib.sha256(contents).hexdigest()
        if not secrets.compare_digest(actual, expected):
            raise ValueError(f"{MODEL_DIGEST_ENV} does not match the checkpoint.")
    elif os.getenv("AERM_ENV", "development").strip().lower() in {"production", "prod"}:
        raise ValueError(f"{MODEL_DIGEST_ENV} is required in production.")
    model = pickle.loads(contents)
    if not hasattr(model, "predict") or not hasattr(model, "decision_function"):
        raise ValueError("The configured checkpoint is not a compatible SVM classifier.")
    return model


def _validate_image_bytes(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("The image-quality model could not decode the image.") from exc


def assess_images(images: list[tuple[str, bytes]]) -> dict | None:
    model_path = os.getenv(MODEL_ENV)
    if not model_path:
        return None
    if not Path(model_path).is_file():
        raise FileNotFoundError(
            f"{MODEL_ENV} points to a missing checkpoint: {model_path}"
        )

    model = _load_model(model_path)
    assessments = []
    for view, content in images:
        _validate_image_bytes(content)
        values = extract_features_from_bytes(content)[None, :]
        predicted = int(model.predict(values)[0])
        score = float(model.decision_function(values)[0])
        assessments.append(
            {
                "view": view,
                "label": "quality_sufficient" if predicted else "insufficient",
                "decision_score": score,
                "score_kind": "decision_score",
            }
        )
    return {
        "available": True,
        "model": MODEL_NAME,
        "views": assessments,
        "notice": (
            "Image-gradability only. This model does not predict skin type, "
            "acne, hydration, sebum, allergies, barrier health, or diagnosis."
        ),
    }
