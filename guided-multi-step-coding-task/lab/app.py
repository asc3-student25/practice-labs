from flask import Flask, jsonify, request

from storage import TaskStore

app = Flask(__name__)
store = TaskStore()
ALLOWED_STATUSES = {"pending", "in_progress", "done"}


def error_response(message, status_code, **extra):
    body = {"error": message}
    body.update(extra)
    return jsonify(body), status_code


def validate_task_payload(data, require_title=False):
    if not isinstance(data, dict):
        return "invalid JSON payload", 400, {}

    if require_title and "title" not in data:
        return "title is required", 400, {}

    if "title" in data:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return "title must be a non-empty string", 400, {}

    if "status" in data and data.get("status") not in ALLOWED_STATUSES:
        return (
            "status must be one of: pending, in_progress, done",
            422,
            {"valid_statuses": sorted(ALLOWED_STATUSES)},
        )

    return None, None, {}


@app.route("/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    if status is None:
        tasks = store.list_all()
    elif status in ALLOWED_STATUSES:
        tasks = store.list_all(status=status)
    else:
        tasks = []

    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = store.get(task_id)
    if task is None:
        return error_response("task not found", 404)
    return jsonify(task), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    error, status_code, extra = validate_task_payload(data, require_title=True)
    if error:
        return error_response(error, status_code, **extra)

    task = store.create(
        title=data.get("title").strip(),
        status=data.get("status", "pending"),
    )
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    if store.get(task_id) is None:
        return error_response("task not found", 404)

    data = request.get_json(silent=True) or {}
    error, status_code, extra = validate_task_payload(data, require_title=False)
    if error:
        return error_response(error, status_code, **extra)

    updated = store.update(
        task_id,
        title=data["title"].strip() if "title" in data else None,
        status=data.get("status"),
    )
    return jsonify(updated), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    deleted = store.delete(task_id)
    if not deleted:
        return error_response("task not found", 404)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
