from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def ping(self):
        self.client.get("/ping")

    @task
    def get_data(self):
        self.client.get("/data")

    @task
    def unstable(self):
        self.client.get("/unstable")
