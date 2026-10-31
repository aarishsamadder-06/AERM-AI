from pathlib import Path

import numpy as np
from PIL import Image

from ml.quality_baseline import _label_from_gradability, extract_features


def test_gradability_policy_maps_quality_variants_and_rejects_ties():
    assert _label_from_gradability(
        {
            "dermatologist_gradable_for_skin_condition_1": "DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT",
            "dermatologist_gradable_for_skin_condition_2": "YES_IMAGE_QUALITY_SUFFICIENT_NO_DISCERNIBLE_PATHOLOGY",
        }
    ) == "quality_sufficient"
    assert _label_from_gradability(
        {
            "dermatologist_gradable_for_skin_condition_1": "NO_IMAGE_QUALITY_INSUFFICIENT",
        }
    ) == "insufficient"
    assert _label_from_gradability(
        {
            "dermatologist_gradable_for_skin_condition_1": "NO_IMAGE_QUALITY_INSUFFICIENT",
            "dermatologist_gradable_for_skin_condition_2": "DEFAULT_YES_IMAGE_QUALITY_SUFFICIENT",
            "dermatologist_gradable_for_skin_condition_3": "NO_IMAGE_QUALITY_INSUFFICIENT",
        }
    ) == "ambiguous"


def test_extract_features_is_finite_and_fixed_length(tmp_path: Path):
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (160, 120), (120, 80, 60)).save(image_path)
    values = extract_features(image_path)
    assert values.shape == (21,)
    assert np.isfinite(values).all()
