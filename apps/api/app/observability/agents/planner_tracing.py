from time import perf_counter

from app.observability.metrics import PLANNER_EXECUTION_DURATION_MS, elapsed_ms


class PlannerTracing:
    def start_timer(self) -> float:
        return perf_counter()

    def record(self, planner: str, status: str, start_time: float) -> None:
        PLANNER_EXECUTION_DURATION_MS.labels(planner, status).observe(elapsed_ms(start_time))
