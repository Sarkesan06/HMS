from flask import Blueprint, request, jsonify
from app import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_mail import Message
from app import mail
from config import Config
from threading import Thread
import resend

# Try to import ML models, but don't fail if not available
try:
    from app.ml_models import appointment_predictor, demand_predictor, disease_predictor
    ML_AVAILABLE = True
except ImportError:
    # Create dummy objects if ML models not available
    class DummyPredictor:
        def predict_no_show_risk(self, *args, **kwargs): return 30
        def predict_daily_load(self, *args, **kwargs): return 8
        def predict_demand(self, *args, **kwargs): return [5] * 7
    
    appointment_predictor = DummyPredictor()
    demand_predictor = DummyPredictor()
    disease_predictor = None
    ML_AVAILABLE = False
    print("⚠️ ML models not available, using dummy predictors")
import numpy as np

appointment_bp = Blueprint("appointment_bp", __name__)

# ================= GET ALL APPOINTMENTS =================
@appointment_bp.route("/all", methods=["GET"])
# @jwt_required()  # Commented for testing
def get_appointments():
    try:
        appointments = list(mongo.db.appointments.find().sort("created_at", -1))
        
        for a in appointments:
            a["_id"] = str(a["_id"])
        
        return jsonify(appointments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ================= UPDATE STATUS =================
@appointment_bp.route("/status/<id>", methods=["PUT"])
def update_status(id):
    try:
        data = request.get_json()
        
        mongo.db.appointments.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": data.get("status")}}
        )
        
        return jsonify({"message": "Status updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= DELETE APPOINTMENT =================
@appointment_bp.route("/<id>", methods=["DELETE"])
def delete_appointment(id):
    try:
        mongo.db.appointments.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================= REPORTS =================
# ================= REPORTS =================
@appointment_bp.route("/report/doctors", methods=["GET"])
@jwt_required()
def doctor_report():
    try:
        total_doctors = mongo.db.doctors.count_documents({})
        print(f"Total doctors: {total_doctors}")
        return jsonify({"total_doctors": total_doctors}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/patients", methods=["GET"])
@jwt_required()
def patient_report():
    try:
        total_patients = mongo.db.patients.count_documents({})
        print(f"Total patients: {total_patients}")
        return jsonify({"total_patients": total_patients}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/appointments", methods=["GET"])
@jwt_required()
def appointment_report():
    try:
        total = mongo.db.appointments.count_documents({})
        completed = mongo.db.appointments.count_documents({"status": "Completed"})
        pending = mongo.db.appointments.count_documents({"status": "Pending"})
        cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
        
        print(f"Appointment stats - Total: {total}, Completed: {completed}, Pending: {pending}, Cancelled: {cancelled}")
        
        return jsonify({
            "total": total,
            "completed": completed,
            "pending": pending,
            "cancelled": cancelled
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/chart", methods=["GET"])
@jwt_required()
def chart_data():
    try:
        from collections import Counter
        
        appointments = list(mongo.db.appointments.find())
        
        # Daily appointments
        days = [a.get("date", "Unknown") for a in appointments]
        day_count = Counter(days)
        
        # Status counts
        completed = mongo.db.appointments.count_documents({"status": "Completed"})
        pending = mongo.db.appointments.count_documents({"status": "Pending"})
        cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
        
        result = {
            "days": list(day_count.keys()),
            "counts": list(day_count.values()),
            "status": {
                "completed": completed,
                "pending": pending,
                "cancelled": cancelled
            }
        }
        
        print(f"Chart data - Days: {len(result['days'])}, Status: {result['status']}")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/monthly", methods=["GET"])
@jwt_required()
def monthly_report():
    try:
        from collections import Counter
        
        appointments = list(mongo.db.appointments.find())
        months = []
        
        for a in appointments:
            date = a.get("date", "")
            if date and len(date) >= 7:
                months.append(date[:7])  # YYYY-MM
        
        month_count = Counter(months)
        result = [{"month": k, "count": v} for k, v in sorted(month_count.items())]
        
        print(f"Monthly data: {len(result)} months")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/doctor-performance", methods=["GET"])
@jwt_required()
def doctor_performance():
    try:
        from collections import Counter
        
        appointments = list(mongo.db.appointments.find())
        doctors = [a.get("doctor", "Unknown") for a in appointments]
        count = Counter(doctors)
        result = [{"doctor": k, "count": v} for k, v in count.items()]
        
        print(f"Doctor performance: {len(result)} doctors")
        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/report/predict", methods=["GET"])
@jwt_required()
def predict_busy_day():
    try:
        from collections import Counter
        
        appointments = list(mongo.db.appointments.find())
        days = [a.get("date", "") for a in appointments if a.get("date")]
        
        if not days:
            return jsonify({"message": "No data available"}), 200
        
        count = Counter(days)
        busy_day = max(count, key=count.get)
        
        return jsonify({
            "busy_day": busy_day,
            "appointments": count[busy_day]
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500



@appointment_bp.route("/my-appointments", methods=["GET"])
@jwt_required()
def get_my_appointments():
    try:
        current_user_email = get_jwt_identity()
        print(f"📅 Getting appointments for patient: {current_user_email}")
        
        # Find patient by email
        patient = mongo.db.patients.find_one({"email": current_user_email})
        if not patient:
            print(f"❌ Patient not found: {current_user_email}")
            return jsonify({"error": "Patient not found"}), 404
        
        # Get appointments for this patient
        appointments = list(mongo.db.appointments.find({
            "$or": [
                {"patient_email": current_user_email},
                {"patient_id": str(patient["_id"])}
            ]
        }).sort("date", -1))
        
        print(f"✅ Found {len(appointments)} appointments for {current_user_email}")
        
        for a in appointments:
            a["_id"] = str(a["_id"])
        
        return jsonify(appointments), 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@appointment_bp.route("/reschedule/<id>", methods=["PUT"])
@jwt_required()
def reschedule_appointment(id):
    try:
        data = request.get_json()
        new_date = data.get("date")
        new_time = data.get("time")
        
        if not new_date or not new_time:
            return jsonify({"message": "New date and time are required"}), 400
        
        # Get appointment
        appointment = mongo.db.appointments.find_one({"_id": ObjectId(id)})
        if not appointment:
            return jsonify({"message": "Appointment not found"}), 404
        
        # Check if new slot is available
        existing = mongo.db.appointments.find_one({
            "doctor_id": appointment["doctor_id"],
            "date": new_date,
            "time": new_time,
            "status": {"$ne": "Cancelled"},
            "_id": {"$ne": ObjectId(id)}
        })
        
        if existing:
            return jsonify({"message": "This time slot is already booked"}), 409
        
        # Update appointment
        result = mongo.db.appointments.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "date": new_date,
                "time": new_time,
                "status": "Pending",
                "rescheduled_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            return jsonify({"message": "Appointment not found or no changes made"}), 404
        
        return jsonify({"message": "Appointment rescheduled successfully"}), 200
        
    except Exception as e:
        print(f"Error rescheduling: {str(e)}")
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/doctor-appointments", methods=["GET"])
@jwt_required()
def get_doctor_appointments():
    try:
        current_user_email = get_jwt_identity()
        print(f"Getting appointments for doctor: {current_user_email}")
        
        # Find doctor by email
        doctor = mongo.db.doctors.find_one({"email": current_user_email})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        
        # Get all appointments for this doctor
        appointments = list(mongo.db.appointments.find({
            "doctor_id": str(doctor["_id"])
        }).sort("date", -1))
        
        for a in appointments:
            a["_id"] = str(a["_id"])
        
        print(f"Found {len(appointments)} appointments for doctor")
        return jsonify(appointments), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    


# Add these new routes to appointment.py

# ================= ML PREDICTION ENDPOINTS =================

@appointment_bp.route("/predict/no-show/<appointment_id>", methods=["GET"])
@jwt_required()
def predict_no_show(appointment_id):
    """Predict risk of patient not showing up"""
    try:
        appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
        
        if not appointment:
            return jsonify({"message": "Appointment not found"}), 404
        
        risk = appointment_predictor.predict_no_show_risk(appointment)
        
        # Determine risk level
        if risk >= 70:
            level = "High"
            recommendation = "Send reminder SMS/Email, consider overbooking"
        elif risk >= 40:
            level = "Medium"
            recommendation = "Send reminder notification"
        else:
            level = "Low"
            recommendation = "Standard confirmation is sufficient"
        
        return jsonify({
            "appointment_id": appointment_id,
            "no_show_risk": risk,
            "risk_level": level,
            "recommendation": recommendation,
            "patient_name": appointment.get("patient"),
            "date": appointment.get("date"),
            "time": appointment.get("time")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/predict/daily-load", methods=["POST"])
@jwt_required()
def predict_daily_load():
    """Predict appointment load for a specific date"""
    try:
        data = request.get_json()
        date = data.get("date")
        
        if not date:
            return jsonify({"message": "Date required"}), 400
        
        predicted_load = appointment_predictor.predict_daily_load(date)
        
        # Get current load for comparison
        current_count = mongo.db.appointments.count_documents({"date": date})
        
        # Calculate capacity percentage (assuming 20 appointments max per day)
        capacity = 20
        capacity_percentage = min(100, int((predicted_load / capacity) * 100))
        
        # Determine status
        if capacity_percentage >= 80:
            status = "Critical - High Load Expected"
            recommendation = "Consider adding more doctors or extending hours"
        elif capacity_percentage >= 60:
            status = "Busy - Moderate Load Expected"
            recommendation = "Ensure adequate staffing"
        else:
            status = "Normal - Manageable Load"
            recommendation = "Standard operations"
        
        return jsonify({
            "date": date,
            "predicted_appointments": predicted_load,
            "current_booked": current_count,
            "capacity_percentage": capacity_percentage,
            "status": status,
            "recommendation": recommendation,
            "available_slots": max(0, capacity - current_count)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/predict/demand", methods=["GET"])
@jwt_required()
def predict_demand():
    """Predict appointment demand for next 7 days"""
    try:
        days = request.args.get("days", 7, type=int)
        days = min(days, 30)  # Limit to 30 days
        
        predictions = demand_predictor.predict_demand(days)
        
        # Generate dates for predictions
        from datetime import datetime, timedelta
        start_date = datetime.now()
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, days + 1)]
        
        # Create detailed response
        demand_forecast = []
        for i, (date, pred) in enumerate(zip(dates, predictions)):
            demand_forecast.append({
                "date": date,
                "predicted_appointments": pred,
                "day_of_week": datetime.strptime(date, '%Y-%m-%d').strftime('%A'),
                "peak_hour_prediction": "10:00 AM - 12:00 PM" if pred > 10 else "Distributed throughout day"
            })
        
        # Calculate summary statistics
        total_predicted = sum(predictions)
        avg_daily = total_predicted / days
        
        return jsonify({
            "forecast_period_days": days,
            "total_predicted_appointments": total_predicted,
            "average_daily": round(avg_daily, 1),
            "peak_day": max(demand_forecast, key=lambda x: x['predicted_appointments']),
            "daily_forecast": demand_forecast
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/predict/optimal-time", methods=["POST"])
@jwt_required()
def predict_optimal_time():
    """Suggest optimal appointment time based on historical patterns"""
    try:
        data = request.get_json()
        preferred_date = data.get("preferred_date")
        doctor_id = data.get("doctor_id")
        
        # Get historical data for this doctor
        appointments = list(mongo.db.appointments.find({
            "doctor_id": doctor_id,
            "status": {"$ne": "Cancelled"}
        }))
        
        if len(appointments) < 10:
            return jsonify({
                "recommended_times": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM"],
                "message": "Insufficient data for optimal prediction. Showing standard slots."
            }), 200
        
        # Analyze busy hours
        hour_counts = {}
        for appt in appointments:
            time_str = appt.get("time", "")
            if time_str:
                # Extract hour
                try:
                    hour = int(time_str.split(":")[0])
                    period = time_str.split()[1] if len(time_str.split()) > 1 else "AM"
                    hour_12 = hour % 12
                    if period == "PM" and hour_12 != 12:
                        hour_24 = hour_12 + 12
                    elif period == "AM" and hour_12 == 12:
                        hour_24 = 0
                    else:
                        hour_24 = hour_12
                    
                    hour_counts[hour_24] = hour_counts.get(hour_24, 0) + 1
                except:
                    pass
        
        # Find least busy hours
        if hour_counts:
            avg_per_hour = sum(hour_counts.values()) / len(hour_counts)
            optimal_hours = [h for h, count in hour_counts.items() if count < avg_per_hour]
            
            # Convert back to readable time
            time_slots = []
            for hour in sorted(optimal_hours)[:5]:  # Top 5 optimal hours
                if hour == 0:
                    time_slots.append("12:00 AM")
                elif hour < 12:
                    time_slots.append(f"{hour}:00 AM")
                elif hour == 12:
                    time_slots.append("12:00 PM")
                else:
                    time_slots.append(f"{hour-12}:00 PM")
        else:
            time_slots = ["9:00 AM", "11:00 AM", "2:00 PM", "4:00 PM"]
        
        return jsonify({
            "recommended_times": time_slots,
            "message": "These times typically have lower patient volume",
            "based_on": f"Analysis of {len(appointments)} past appointments"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/insights/doctor-performance", methods=["GET"])
@jwt_required()
def doctor_performance_insights():
    """Get ML-based insights about doctor performance"""
    try:
        # Get all completed appointments
        appointments = list(mongo.db.appointments.find({"status": "Completed"}))
        
        if len(appointments) < 20:
            return jsonify({"message": "Insufficient data for insights"}), 200
        
        # Analyze doctor performance
        doctor_stats = {}
        for appt in appointments:
            doctor = appt.get("doctor", "Unknown")
            if doctor not in doctor_stats:
                doctor_stats[doctor] = {
                    "total": 0,
                    "by_day": {i: 0 for i in range(7)},
                    "by_hour": {}
                }
            
            doctor_stats[doctor]["total"] += 1
            
            # Day of week analysis
            try:
                date = datetime.strptime(appt.get("date", "2024-01-01"), "%Y-%m-%d")
                doctor_stats[doctor]["by_day"][date.weekday()] += 1
            except:
                pass
            
            # Hour analysis
            time_str = appt.get("time", "")
            if time_str:
                try:
                    hour = int(time_str.split(":")[0])
                    doctor_stats[doctor]["by_hour"][hour] = doctor_stats[doctor]["by_hour"].get(hour, 0) + 1
                except:
                    pass
        
        # Generate insights
        insights = []
        for doctor, stats in doctor_stats.items():
            total = stats["total"]
            
            # Find busiest day
            busiest_day = max(stats["by_day"], key=stats["by_day"].get)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Find busiest hour
            if stats["by_hour"]:
                busiest_hour = max(stats["by_hour"], key=stats["by_hour"].get)
                peak_time = f"{busiest_hour}:00 {'AM' if busiest_hour < 12 else 'PM'}"
            else:
                peak_time = "Not enough data"
            
            insights.append({
                "doctor": doctor,
                "total_appointments": total,
                "busiest_day": days[busiest_day],
                "peak_time": peak_time,
                "productivity_score": min(100, int((total / 50) * 100)),  # Assuming 50 is high
                "recommendation": "Consider adjusting schedule" if total < 20 else "Maintain current schedule"
            })
        
        # Sort by productivity
        insights.sort(key=lambda x: x["productivity_score"], reverse=True)
        
        return jsonify({
            "insights": insights,
            "total_analyzed": len(appointments),
            "analysis_period": "All time"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# Add these imports at the top if not already present


# ================= DOCTOR APPOINTMENT ENDPOINTS =================

@appointment_bp.route("/doctor/daily-appointments", methods=["GET"])
@jwt_required()
def get_doctor_daily_appointments():
    """Get today's appointments for the logged-in doctor"""
    try:
        current_user_email = get_jwt_identity()
        print(f"Fetching daily appointments for doctor: {current_user_email}")
        
        # Find the doctor
        doctor = mongo.db.doctors.find_one({"email": current_user_email})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        
        doctor_name = doctor.get("name")
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        today_formatted = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get today's appointments for this doctor
        todays_appointments = list(mongo.db.appointments.find({
            "doctor": doctor_name,
            "date": today
        }).sort("time", 1))
        
        # Get upcoming appointments (next 7 days)
        upcoming_appointments = []
        for i in range(1, 8):
            future_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            day_appts = list(mongo.db.appointments.find({
                "doctor": doctor_name,
                "date": future_date,
                "status": "Pending"
            }).sort("time", 1))
            upcoming_appointments.extend(day_appts)
        
        # Get appointment statistics
        total_today = len(todays_appointments)
        completed_today = sum(1 for a in todays_appointments if a.get("status") == "Completed")
        pending_today = sum(1 for a in todays_appointments if a.get("status") == "Pending")
        cancelled_today = sum(1 for a in todays_appointments if a.get("status") == "Cancelled")
        
        # Prepare response
        appointments_list = []
        for appt in todays_appointments:
            appointments_list.append({
                "id": str(appt["_id"]),
                "patient": appt.get("patient", "Unknown"),
                "patient_id": appt.get("patient_id", ""),
                "time": appt.get("time", "N/A"),
                "status": appt.get("status", "Pending"),
                "priority": appt.get("priority", "Normal"),
                "type": appt.get("type", "offline"),
                "date": appt.get("date", today)
            })
        
        upcoming_list = []
        for appt in upcoming_appointments:
            upcoming_list.append({
                "id": str(appt["_id"]),
                "patient": appt.get("patient", "Unknown"),
                "date": appt.get("date", ""),
                "time": appt.get("time", "N/A"),
                "status": appt.get("status", "Pending"),
                "priority": appt.get("priority", "Normal")
            })
        
        return jsonify({
            "doctor_name": doctor_name,
            "doctor_specialization": doctor.get("specialization", "General Medicine"),
            "today_date": today,
            "today_formatted": today_formatted,
            "total_today": total_today,
            "completed_today": completed_today,
            "pending_today": pending_today,
            "cancelled_today": cancelled_today,
            "completion_rate": round((completed_today / total_today * 100), 1) if total_today > 0 else 0,
            "appointments": appointments_list,
            "upcoming_appointments": upcoming_list,
            "upcoming_count": len(upcoming_list)
        }), 200
        
    except Exception as e:
        print(f"Error in get_doctor_daily_appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/doctor/update-status/<appointment_id>", methods=["PUT"])
@jwt_required()
def update_appointment_status_by_doctor(appointment_id):
    """Doctor updates appointment status (Complete/Cancel)"""
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        new_status = data.get("status")
        
        if not new_status:
            return jsonify({"error": "Status is required"}), 400
        
        # Verify doctor
        doctor = mongo.db.doctors.find_one({"email": current_user_email})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        
        # Get appointment
        appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
        
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        
        # Verify this appointment belongs to the doctor
        if appointment.get("doctor") != doctor.get("name"):
            return jsonify({"error": "You can only update your own appointments"}), 403
        
        # Update status
        result = mongo.db.appointments.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": {
                "status": new_status, 
                "updated_by": doctor.get("name"), 
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({
                "message": f"Appointment marked as {new_status}",
                "status": "success"
            }), 200
        else:
            return jsonify({"error": "Failed to update appointment"}), 500
        
    except Exception as e:
        print(f"Error in update_appointment_status_by_doctor: {str(e)}")
        return jsonify({"error": str(e)}), 500


@appointment_bp.route("/doctor/weekly-schedule", methods=["GET"])
@jwt_required()
def get_doctor_weekly_schedule():
    """Get doctor's complete weekly schedule"""
    try:
        current_user_email = get_jwt_identity()
        
        # Find the doctor
        doctor = mongo.db.doctors.find_one({"email": current_user_email})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        
        doctor_name = doctor.get("name")
        
        # Get next 7 days
        weekly_schedule = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            day_name = (datetime.now() + timedelta(days=i)).strftime('%A')
            
            appointments = list(mongo.db.appointments.find({
                "doctor": doctor_name,
                "date": date
            }).sort("time", 1))
            
            details = []
            for appt in appointments:
                details.append({
                    "time": appt.get("time", "N/A"),
                    "patient": appt.get("patient", "Unknown"),
                    "status": appt.get("status", "Pending"),
                    "type": appt.get("type", "offline")
                })
            
            weekly_schedule.append({
                "date": date,
                "day": day_name,
                "appointments": len(appointments),
                "details": details
            })
        
        return jsonify({
            "doctor_name": doctor_name,
            "doctor_specialization": doctor.get("specialization", "General Medicine"),
            "weekly_schedule": weekly_schedule
        }), 200
        
    except Exception as e:
        print(f"Error in get_doctor_weekly_schedule: {str(e)}")
        return jsonify({"error": str(e)}), 500
    






# ================= CONFIRMATION EMAIL FUNCTION =================
def send_booking_confirmation_email(patient_email, patient_name, doctor_name, appointment_date, appointment_time, appointment_id, consult_type):
    """Send booking confirmation email with appointment ID"""
    
    if not patient_email:
        print("❌ No patient email provided")
        return False
    
    # Format date for better display
    try:
        date_obj = datetime.strptime(appointment_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %B %d, %Y')
    except:
        formatted_date = appointment_date
    
    subject = "✅ Appointment Confirmation - Hospital Management System"
    
    # Create HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1d3557, #457b9d); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
            .appointment-details {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2a9d8f; }}
            .appointment-id {{ background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 18px; font-weight: bold; text-align: center; margin: 10px 0; }}
            .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; }}
            .button {{ background: #2a9d8f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏥 Hospital Management System</h2>
                <p>Appointment Confirmation</p>
            </div>
            <div class="content">
                <p>Dear <strong>{patient_name}</strong>,</p>
                
                <p>Your appointment has been successfully booked! Please find the details below:</p>
                
                <div class="appointment-details">
                    <h3 style="margin: 0 0 10px 0; color: #1d3557;">📋 Appointment Details:</h3>
                    <p><strong>🆔 Appointment ID:</strong></p>
                    <div class="appointment-id">{appointment_id}</div>
                    <p><strong>👨‍⚕️ Doctor:</strong> Dr. {doctor_name}<br>
                    <strong>📅 Date:</strong> {formatted_date}<br>
                    <strong>🕐 Time:</strong> {appointment_time}<br>
                    <strong>🎥 Consultation Type:</strong> {"🎥 Video Consultation" if consult_type == "online" else "🏥 Hospital Visit"}</p>
                </div>
                
                {"<div style='background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;'><strong>📌 For Video Consultation:</strong><br>Use the Appointment ID above to join the call from the Consultation page.<br><br><a href='https://meet.jit.si/HMS_" + appointment_id + "' class='button'>🎥 Join Video Call</a></div>" if consult_type == "online" else ""}
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <strong>⚠️ Important Notes:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>You will receive a reminder email 5 minutes before your appointment</li>
                        <li>Please arrive 10 minutes early for in-person consultations</li>
                        <li>For video consultations, ensure stable internet connection</li>
                        <li>Keep your Appointment ID handy for reference</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{Config.FRONTEND_URL}" class="button">📅 View My Appointments</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2024 Hospital Management System | All Rights Reserved</p>
                <p>This is an automated confirmation, please do not reply.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    text_body = f"""
Hospital Management System - Appointment Confirmation

Dear {patient_name},

Your appointment has been successfully booked!

Appointment Details:
🆔 Appointment ID: {appointment_id}
👨‍⚕️ Doctor: Dr. {doctor_name}
📅 Date: {formatted_date}
🕐 Time: {appointment_time}
🎥 Type: {"Video Consultation" if consult_type == "online" else "Hospital Visit"}

{"For Video Consultation, use this link: https://meet.jit.si/HMS_" + appointment_id if consult_type == "online" else ""}

You will receive a reminder email 5 minutes before your appointment.

Thank you for choosing our hospital!
"""
    
    def _send():
        try:
            if Config.RESEND_API_KEY and Config.RESEND_FROM_EMAIL:
                resend.api_key = Config.RESEND_API_KEY
                response = resend.Emails.send({
                    "from": Config.RESEND_FROM_EMAIL,
                    "to": [patient_email],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                })
                print(f"✅ Booking confirmation email sent via Resend to {patient_email}: {response}")
                return

            msg = Message(
                subject=subject,
                recipients=[patient_email],
                body=text_body,
                html=html_body,
                sender=Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME or "sharkroshan@gmail.com"
            )
            mail.send(msg)
            print(f"✅ Booking confirmation email sent to {patient_email} for appointment {appointment_id}")
        except Exception as e:
            print(f"❌ Failed to send booking confirmation: {str(e)}")

    try:
        Thread(target=_send, daemon=True).start()
        return True
    except Exception as e:
        print(f"❌ Failed to queue booking confirmation: {str(e)}")
        return False

# ================= BOOK APPOINTMENT =================
@appointment_bp.route("/book", methods=["POST"])
def book_appointment():
    try:
        data = request.get_json()
        
        print("=" * 50)
        print("📅 Booking new appointment...")
        print(f"Patient email from request: {data.get('patient_email')}")
        
        # Get patient email - try multiple sources
        patient_email = data.get("patient_email")
        patient_id = data.get("patient_id")
        patient_name = data.get("patient_name", "Patient")
        
        # If no email in request, try to get from patients collection
        if not patient_email and patient_id:
            try:
                patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
                if patient:
                    patient_email = patient.get("email")
                    patient_name = patient.get("name", patient_name)
                    print(f"✅ Found patient email from database: {patient_email}")
            except Exception as e:
                print(f"Error finding patient: {e}")
        
        # If still no email, try to get from logged in user
        if not patient_email:
            try:
                current_user = get_jwt_identity()
                if current_user and '@' in current_user:
                    patient_email = current_user
                    print(f"✅ Using logged in user email: {patient_email}")
            except:
                pass
        
        # Create appointment document
        appointment = {
            "doctor_id": data.get("doctor_id"),
            "doctor": data.get("doctor_name"),
            "patient_id": patient_id,
            "patient": patient_name,
            "patient_email": patient_email,  # Store email in appointment
            "date": data.get("date"),
            "time": data.get("time"),
            "priority": data.get("priority", "Normal"),
            "status": "Pending",
            "type": data.get("type", "offline"),
            "created_at": datetime.utcnow(),
            "reminder_sent": False
        }
        
        # Insert appointment
        result = mongo.db.appointments.insert_one(appointment)
        appointment_id = str(result.inserted_id)
        
        print(f"✅ Appointment created with ID: {appointment_id}")
        print(f"📧 Will send confirmation to: {patient_email}")
        
        # Send confirmation email
        if patient_email:
            email_sent = send_booking_confirmation_email(
                patient_email=patient_email,
                patient_name=patient_name,
                doctor_name=data.get("doctor_name", "Doctor"),
                appointment_date=data.get("date"),
                appointment_time=data.get("time"),
                appointment_id=appointment_id,
                consult_type=data.get("type", "offline")
            )
            
            if email_sent:
                print("✅ Confirmation email sent successfully")
            else:
                print("❌ Failed to send confirmation email")
        else:
            print("⚠️ No email address found - skipping confirmation email")
        
        print("=" * 50)
        
        return jsonify({
            "success": True,
            "message": "Appointment booked successfully",
            "id": appointment_id,
            "email_sent": email_sent if patient_email else False
        }), 201
        
    except Exception as e:
        print(f"❌ Error booking appointment: {str(e)}")
        return jsonify({"error": str(e)}), 500
