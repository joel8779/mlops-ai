def precision_at_k(relevant: list[bool], k: int) -> float:
    if k <= 0:
        return 0.0
    top = relevant[:k]
    return sum(top) / k


def mean_reciprocal_rank(relevant: list[bool]) -> float:
    for index, is_relevant in enumerate(relevant, start=1):
        if is_relevant:
            return 1 / index
    return 0.0


def ndcg_at_k(gains: list[float], k: int) -> float:
    import math

    def dcg(values: list[float]) -> float:
        return sum(value / math.log2(index + 2) for index, value in enumerate(values))

    actual = dcg(gains[:k])
    ideal = dcg(sorted(gains, reverse=True)[:k])
    return actual / ideal if ideal else 0.0
