from locust import HttpUser, task, between


class TodoUser(HttpUser):
    wait_time = between(1, 2)  # mỗi user chờ 1-2s giữa các request
    host = "http://127.0.0.1:3000"

    @task(3)  # tần suất cao hơn vì hay dùng nhất
    def get_todos(self):
        self.client.get("/todos")

    @task(2)
    def get_todo_by_id(self):
        self.client.get("/todos/1")

    @task(1)
    def create_todo(self):
        self.client.post("/todos", json={"title": "Load test item"})

# locust -f locustfile.py
# http://localhost:8089
