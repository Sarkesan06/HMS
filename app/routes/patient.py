from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

patient_bp = Blueprint("patients", __name__, url_prefix="/patients")



# ================= SEARCH PATIENT BY EMAIL =================
@patient_bp.route("/search", methods=["GET"])
@jwt_required()
def search_patient():
    try:
        email = request.args.get("email")
        print(f"🔍 Searching for patient with email: {email}")
        
        if not email:
            return jsonify({"message": "Email parameter required"}), 400
        
        # Find patient by email
        patient = mongo.db.patients.find_one({"email": email})
        
        if not patient:
            print(f"❌ No patient found with email: {email}")
            return jsonify({"message": "Patient not found"}), 404
        
        # Remove password
        if "password" in patient:
            del patient["password"]
        
        # Convert ObjectId to string
        patient["_id"] = str(patient["_id"])
        
        # Ensure all fields exist
        patient["age"] = patient.get("age") if patient.get("age") else "Not specified"
        patient["gender"] = patient.get("gender") if patient.get("gender") else "Not specified"
        patient["phone"] = patient.get("phone") if patient.get("phone") else "Not specified"
        
        print(f"✅ Patient found: {patient.get('name')}")
        return jsonify(patient), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================= UPDATE PATIENT =================
@patient_bp.route("/<id>", methods=["PUT"])
@jwt_required()
def update_patient(id):
    try:
        data = request.get_json()
        print(f"📝 Updating patient {id}: {data}")
        
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "age" in data:
            update_data["age"] = data["age"]
        if "gender" in data:
            update_data["gender"] = data["gender"]
        if "phone" in data:
            update_data["phone"] = data["phone"]
        
        if update_data:
            result = mongo.db.patients.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return jsonify({"message": "Patient not found"}), 404
        
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ================= REGISTER PATIENT =================
@patient_bp.route("/", methods=["POST"])
def register_patient():
    try:
        data = request.get_json()
        
        patient_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "age": data.get("age", ""),
            "gender": data.get("gender", ""),
            "phone": data.get("phone", ""),
            "role": "patient",
            "created_at": datetime.utcnow()
        }
        
        result = mongo.db.patients.insert_one(patient_data)
        
        return jsonify({
            "message": "Patient registered successfully",
            "id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ================= GET DOCTOR'S PATIENTS =================
@patient_bp.route("/my-patients", methods=["GET"])
@jwt_required()
def get_my_patients():
    try:
        current_user_email = get_jwt_identity()
        print(f"🔍 Getting patients for doctor: {current_user_email}")
        
        # Get all appointments for this doctor
        appointments = list(mongo.db.appointments.find({"doctor_email": current_user_email}))
        
        # Get unique patient IDs from appointments
        patient_ids = list(set([a.get("patient_id") for a in appointments if a.get("patient_id")]))
        
        patients = []
        for pid in patient_ids:
            try:
                patient = mongo.db.patients.find_one({"_id": ObjectId(pid)})
                if patient:
                    if "password" in patient:
                        del patient["password"]
                    patient["_id"] = str(patient["_id"])
                    patients.append(patient)
            except:
                pass
        
        print(f"✅ Found {len(patients)} patients for doctor")
        return jsonify(patients), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    


@patient_bp.route("/", methods=["GET"])
@jwt_required()
def get_all_patients():
    try:
        current_user = get_jwt_identity()
        print(f"Getting patients for user: {current_user}")
        
        # Allow access to admin and doctors
        admin = mongo.db.admins.find_one({"email": current_user})
        doctor = mongo.db.doctors.find_one({"email": current_user})
        
        if not admin and not doctor:
            return jsonify([]), 200  # Return empty array instead of error
        
        patients = list(mongo.db.patients.find({}, {"password": 0}))
        
        # Convert ObjectId to string
        for p in patients:
            p["_id"] = str(p["_id"])
        
        print(f"Returning {len(patients)} patients")
        return jsonify(patients), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify([]), 200


@patient_bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_patient(id):
    try:
        current_user = get_jwt_identity()
        
        # Check if user is admin
        admin = mongo.db.admins.find_one({"email": current_user})
        if not admin:
            return jsonify({"message": "Access denied. Admin only!"}), 403
        
        # Delete patient
        result = mongo.db.patients.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count > 0:
            # Delete patient's appointments
            mongo.db.appointments.delete_many({"patient_id": id})
            return jsonify({"message": "Patient deleted successfully"}), 200
        else:
            return jsonify({"message": "Patient not found"}), 404
    except Exception as e:
        print(f"Error deleting patient: {str(e)}")
        return jsonify({"error": str(e)}), 500