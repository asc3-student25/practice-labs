from itertools import count


class TaskStore:
    def __init__(self):
        self._tasks = {}
        self._ids = count(1)

    def create(self, title, status="pending"):
        task_id = next(self._ids)
        task = {"id": task_id, "title": title, "status": status}
        self._tasks[task_id] = task
        return task

    def get(self, task_id):
        return self._tasks.get(task_id)

    def update(self, task_id, title=None, status=None):
        task = self._tasks.get(task_id)
        if task is None:
            return None
        if title is not None:
            task["title"] = title
        if status is not None:
            task["status"] = status
        return task

    def delete(self, task_id):
        return self._tasks.pop(task_id, None) is not None

    def list_all(self, status=None):
        tasks = self._tasks.values()
        if status is not None:
            tasks = [t for t in tasks if t["status"] == status]
        return list(tasks)
