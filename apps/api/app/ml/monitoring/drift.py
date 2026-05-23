from statistics import mean, pstdev


def embedding_drift_score(reference_norms: list[float], current_norms: list[float]) -> float:
    if not reference_norms or not current_norms:
        return 0.0
    reference_mean = mean(reference_norms)
    reference_std = pstdev(reference_norms) or 1.0
    return abs(mean(current_norms) - reference_mean) / reference_std


def drift_status(score: float, warning_threshold: float = 2.0, critical_threshold: float = 3.0) -> str:
    if score >= critical_threshold:
        return "critical"
    if score >= warning_threshold:
        return "warning"
    return "healthy"
