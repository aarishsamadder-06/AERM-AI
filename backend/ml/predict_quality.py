"""Run the saved offline SCIN image-gradability model on one local image."""

from __future__ import annotations

import argparse
from pathlib import Path

from .quality_baseline import predict_image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    args = parser.parse_args()

    if not args.checkpoint.is_file():
        parser.error(f"Checkpoint does not exist: {args.checkpoint}")
    if not args.image.is_file():
        parser.error(f"Image does not exist: {args.image}")

    result = predict_image(args.checkpoint, args.image)
    print(f"Image: {args.image}")
    print(f"Predicted class: {result['label']}")
    print(f"Decision score: {result['score']:.6f}")
    print("Score interpretation: SVM decision score; not a calibrated probability.")


if __name__ == "__main__":
    main()
