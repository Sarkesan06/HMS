from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson import ObjectId

user_bp = Blueprint("user", __name__, url_prefix="/users")

# 🔹 Get All Users (Admin only)
@user_bp.route("/", methods=["GET"])
@jwt_required()
def get_users():
    users = list(mongo.db.users.find({}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return jsonify(users)

# 🔹 Get Single User
@user_bp.route("/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)}, {"password": 0})
    if not user:
        return jsonify({"message": "User not found"}), 404
    user["_id"] = str(user["_id"])
    return jsonify(user)

# 🔹 Update User
@user_bp.route("/<id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    data = request.get_json()

    mongo.db.users.update_one(
        {"_id": ObjectId(id)},
        {"$set": data}
    )

    return jsonify({"message": "User updated successfully"})

# 🔹 Delete User
@user_bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    mongo.db.users.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "User deleted successfully"})