from dataclasses import asdict

from flask import Blueprint, jsonify, request

from backend.store import store

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    if not username or not email:
        return jsonify({"error": "username and email are required"}), 400
    user = store.create(username=username, email=email)
    return jsonify(asdict(user)), 201


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = store.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(asdict(user)), 200


@users_bp.route("", methods=["GET"])
def list_users():
    users = [asdict(user) for user in store.list_all()]
    return jsonify(users), 200
