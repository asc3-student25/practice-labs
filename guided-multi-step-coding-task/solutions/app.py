from flask import Flask, jsonify, request

from storage import TaskStore

app = Flask(__name__)
store = TaskStore()

VALID_STATUSES = {"pending", "in_progress", "done"}


def _validate(data, require_title):
    if require_title:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return "title is required and must be a non-empty string"
    elif "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return "title must be a non-empty string"

    if "status" in data and data["status"] not in VALID_STATUSES:
        return f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"

    return None


@app.route("/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    return jsonify(store.list_all(status=status)), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    error = _validate(data, require_title=True)
    if error:
        return jsonify({"error": error}), 400
    task = store.create(
        title=data["title"].strip(),
        status=data.get("status", "pending"),
    )
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = store.get(task_id)
    if task is None:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    error = _validate(data, require_title=False)
    if error:
        return jsonify({"error": error}), 400
    task = store.update(
        task_id,
        title=data["title"].strip() if "title" in data else None,
        status=data.get("status"),
    )
    if task is None:
        return jsonify({"error": "task not found"}), 404
    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if not store.delete(task_id):
        return jsonify({"error": "task not found"}), 404
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
