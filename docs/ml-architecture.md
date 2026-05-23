# ML Architecture

```mermaid
flowchart LR
  Feedback[Recruiter Feedback] --> Dataset[Ranking Dataset Builder]
  Matches[Candidate Matches] --> Dataset
  Dataset --> Features[Feature Pipeline]
  Features --> Train[XGBoost Pairwise Ranker]
  Train --> MLflow[MLflow Registry]
  MLflow --> Inference[Online Ranker Inference]
  Inference --> API[Matching API]
```

The ranking stack starts with auditable hybrid scoring and upgrades to a learning-to-rank model as feedback volume grows. Recruiter actions become reward labels, while feature snapshots keep training reproducible.
