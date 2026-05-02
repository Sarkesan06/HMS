from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import mongo
from datetime import datetime
from bson.objectid import ObjectId

consultation_bp = Blueprint("consultation", __name__, url_prefix="/consultation")


# ---------------- START CONSULTATION ----------------
@consultation_bp.route("/start", methods=["POST"])
@jwt_required()
def start_consultation():

    data = request.get_json()

    consultation = {
        "appointment_id": data["appointment_id"],
        "doctor_id": data["doctor_id"],
        "patient_id": data["patient_id"],
        "type": "online",
        "status": "Active",
        "messages": [],
        "prescription": "",
        "created_at": datetime.utcnow()
    }

    mongo.db.consultations.insert_one(consultation)

    return jsonify({"message": "Consultation started"})


# ---------------- SEND MESSAGE ----------------
@consultation_bp.route("/chat/<id>", methods=["POST"])
@jwt_required()
def send_message(id):

    data = request.get_json()

    message = {
        "sender": data["sender"],
        "text": data["text"],
        "time": str(datetime.utcnow())
    }

    mongo.db.consultations.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"messages": message}}
    )

    return jsonify({"message": "Message sent"})


# ---------------- GET CHAT ----------------
@consultation_bp.route("/chat/<id>", methods=["GET"])
@jwt_required()
def get_chat(id):

    consult = mongo.db.consultations.find_one({"_id": ObjectId(id)})

    consult["_id"] = str(consult["_id"])

    return jsonify(consult)


# ---------------- PRESCRIPTION ----------------
@consultation_bp.route("/prescription/<id>", methods=["PUT"])
@jwt_required()
def add_prescription(id):

    data = request.get_json()

    mongo.db.consultations.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "prescription": data["prescription"],
            "status": "Completed"
        }}
    )

    return jsonify({"message": "Prescription added"})



# ---------------- CREATE VIDEO ROOM ----------------
@consultation_bp.route("/create/<appointment_id>", methods=["POST"])
@jwt_required()
def create_video_room(appointment_id):

    # Generate unique room
    room = f"HMS_{appointment_id}"

    # Check if already exists
    existing = mongo.db.consultations.find_one({
        "appointment_id": appointment_id
    })

    if existing:
        return jsonify({
            "room": existing["room"],
            "message": "Room already exists"
        })

    consultation = {
        "appointment_id": appointment_id,
        "room": room,
        "status": "Active"
    }

    mongo.db.consultations.insert_one(consultation)

    return jsonify({
        "room": room,
        "message": "Video consultation created"
    })