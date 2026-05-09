from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson.objectid import ObjectId
import traceback

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctors")

# ================= GET ALL DOCTORS (No auth for testing) =================
@doctor_bp.route("/", methods=["GET"])
# @jwt_required()  # Commented out for testing
def get_doctors():
    try:
        print("Getting all doctors...")
        
        # Check if collection exists
        if "doctors" not in mongo.db.list_collection_names():
            print("No doctors collection, creating sample data...")
            sample_doctors = [
                {
                    "name": "Dr. John Smith",
                    "specialization": "Cardiologist",
                    "available_slots": "Mon-Fri 9am-5pm",
                    "email": "john@hospital.com",
                    "role": "doctor"
                },
                {
                    "name": "Dr. Sarah Johnson",
                    "specialization": "Pediatrician",
                    "available_slots": "Mon-Wed 10am-4pm",
                    "email": "sarah@hospital.com",
                    "role": "doctor"
                }
            ]
            mongo.db.doctors.insert_many(sample_doctors)
            print("Sample doctors added!")
        
        # Get all doctors
        doctors = list(mongo.db.doctors.find({}, {"password": 0}))
        print(f"Found {len(doctors)} doctors")
        
        # Convert to JSON serializable format
        result = []
        for doctor in doctors:
            result.append({
                "_id": str(doctor["_id"]),
                "name": doctor.get("name", "Unknown"),
                "specialization": doctor.get("specialization", "Not specified"),
                "available_slots": doctor.get("available_slots", "Not available"),
                "email": doctor.get("email", "")
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in get_doctors: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ================= ADD DOCTOR =================
@doctor_bp.route("/", methods=["POST"])
def add_doctor():
    try:
        data = request.get_json()
        print(f"Adding doctor: {data}")
        
        doctor_data = {
            "name": data.get("name"),
            "specialization": data.get("specialization"),
            "available_slots": data.get("available_slots", ""),
            "email": data.get("email", ""),
            "role": "doctor"
        }
        
        result = mongo.db.doctors.insert_one(doctor_data)
        
        return jsonify({
            "message": "Doctor added successfully",
            "id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================= DELETE DOCTOR =================
@doctor_bp.route("/<id>", methods=["DELETE"])
def delete_doctor(id):
    try:
        result = mongo.db.doctors.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({"message": "Doctor deleted successfully"}), 200
        return jsonify({"message": "Doctor not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@doctor_bp.route("/search", methods=["GET"])
@jwt_required()
def search_doctor():
    try:
        email = request.args.get("email")
        print(f"Searching for doctor with email: {email}")
        
        if not email:
            return jsonify({"message": "Email parameter required"}), 400
        
        doctor = mongo.db.doctors.find_one({"email": email}, {"password": 0})
        
        if not doctor:
            return jsonify({"message": "Doctor not found"}), 404
        
        doctor["_id"] = str(doctor["_id"])
        return jsonify(doctor), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@doctor_bp.route("/<id>", methods=["PUT"])
@jwt_required()
def update_doctor(id):
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        # Allow admin or the doctor themselves to update
        admin = mongo.db.admins.find_one({"email": current_user})
        doctor = mongo.db.doctors.find_one({"email": current_user})
        
        if not admin and (not doctor or str(doctor["_id"]) != id):
            return jsonify({"message": "Access denied"}), 403
        
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "specialization" in data:
            update_data["specialization"] = data["specialization"]
        if "available_slots" in data:
            update_data["available_slots"] = data["available_slots"]
        
        if update_data:
            mongo.db.doctors.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
        
        return jsonify({"message": "Doctor updated successfully"}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500