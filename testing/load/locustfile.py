from locust import HttpUser, between, task


class RecruiterApiUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def readiness(self) -> None:
        self.client.get("/ready", name="ready")

    @task(1)
    def metrics(self) -> None:
        self.client.get("/metrics", name="metrics")
