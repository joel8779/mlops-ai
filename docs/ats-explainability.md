# ATS Explainability

Neural Ops ATS scoring must answer both "what is the score?" and "why did this candidate receive it?"

## Current Scoring Components

`ATSScoringService` returns:

- `ats_score`: total score out of 100.
- `components`: named score components with score, weight, and evidence.
- `issues`: detected weaknesses.
- `recommendations`: recruiter/candidate-facing improvements.
- `explanation`: plain-language summary of strongest and weakest signals.

Current components:

- Section coverage, weighted 30.
- Keyword density, weighted 25.
- Readability, weighted 20.
- Contactability, weighted 15.
- Formatting parseability, weighted 10.

## Required Direction

ATS scoring should become job-aware and combine:

- Keyword matching.
- Semantic similarity.
- Experience matching.
- Skill weighting.
- Education fit.
- Bonus signals.

The matching service already scores several of these against a JD. The next product step is to expose a job-aware ATS endpoint that shares the same evidence model as semantic matching while preserving ATS-specific resume quality checks.

## UI Expectations

Recruiters should see a component breakdown, matched evidence, missing requirements, and recommendations. The UI should never show an unexplained score as the only decision surface.
