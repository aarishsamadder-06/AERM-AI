# Model plan

## Phase 1 (current)

The application uses a deterministic simulator. It hashes the three uploaded image names and bytes, selects a stable skin-signal scenario, and returns educational observations. This makes local demos and tests repeatable without pretending to provide clinical inference.

Images are validated by MIME type, size, and lightweight file signatures, then held in memory only for the request. They are not written to disk or sent to a third-party service.

## Future Phase 2 (not implemented)

If a real model is explored later, the team should first define:

1. A consented, representative, dermatologist-reviewed dataset with documented labels and demographic coverage.
2. Privacy, retention, deletion, and threat-model requirements before collecting any user image.
3. Evaluation for calibration, subgroup performance, false positives/negatives, and robustness to lighting and camera variation.
4. Human oversight, conservative abstention, and clear escalation to qualified clinicians.
5. A versioned inference service with monitoring and a rollback path.

No Phase 2 model, diagnosis, treatment prescription, or clinical claim is part of this repository.
