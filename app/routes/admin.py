from flask import Blueprint, request, jsonify
from app import mongo
from flask_jwt_extended import jwt_required
from app.utils import role_required
from bson.objectid import ObjectId

admin_bp = Blueprint("admin", __name__)


# 🔹 Add Doctor
@admin_bp.route("/add_doctor", methods=["POST"])
@jwt_required()
@role_required("admin")
def add_doctor():
    data = request.json

    doctor = {
        "user_id": data["user_id"],
        "specialization": data["specialization"],
        "available_slots": data["available_slots"]
    }

    mongo.db.doctors.insert_one(doctor)

    return jsonify({"message": "Doctor added successfully"})


# 🔹 Delete Doctor
@admin_bp.route("/delete_doctor/<doctor_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_doctor(doctor_id):

    mongo.db.doctors.delete_one({"_id": ObjectId(doctor_id)})

    return jsonify({"message": "Doctor deleted successfully"})