# ml_dashboard.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app import mongo
from app.ml_models import appointment_predictor, demand_predictor, disease_predictor
from datetime import datetime, timedelta

ml_bp = Blueprint("ml", __name__, url_prefix="/ml")

# Replace the existing ml_dashboard function with this enhanced version

@ml_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def ml_dashboard():
    """Get all ML predictions for dashboard"""
    try:
        from app import mongo
        from datetime import datetime, timedelta
        import numpy as np
        
        # Get predictions for next 7 days
        if demand_predictor:
            demand_forecast = demand_predictor.predict_demand(7)
        else:
            demand_forecast = [5] * 7
        
        # Get current week's dates
        today = datetime.now()
        dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
        
        # Get current bookings for comparison
        daily_bookings = []
        for date in dates:
            count = mongo.db.appointments.count_documents({"date": date})
            daily_bookings.append(count)
        
        # Predict no-show risk for upcoming appointments
        upcoming_appointments = list(mongo.db.appointments.find({
            "date": {"$gte": today.strftime('%Y-%m-%d')},
            "status": "Pending"
        }).limit(50))
        
        high_risk_appointments = []
        medium_risk_appointments = []
        low_risk_appointments = []
        
        for appt in upcoming_appointments:
            if appointment_predictor:
                risk = appointment_predictor.predict_no_show_risk(appt)
            else:
                risk = 30
            
            risk_appt = {
                "patient": appt.get("patient", "Unknown"),
                "date": appt.get("date"),
                "time": appt.get("time"),
                "risk": risk,
                "doctor": appt.get("doctor", "Unknown")
            }
            
            if risk > 60:
                high_risk_appointments.append(risk_appt)
            elif risk > 30:
                medium_risk_appointments.append(risk_appt)
            else:
                low_risk_appointments.append(risk_appt)
        
        # Calculate accuracy metrics
        completed = mongo.db.appointments.count_documents({"status": "Completed"})
        cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
        total_appointments = completed + cancelled
        total_patients = mongo.db.patients.count_documents({})
        total_doctors = mongo.db.doctors.count_documents({})
        
        no_show_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if high_risk_appointments:
            recommendations.append({
                "type": "reminder",
                "message": f"{len(high_risk_appointments)} appointments have high no-show risk. Send reminders immediately.",
                "priority": "High"
            })
        
        # Check for high demand days
        peak_demand = max(demand_forecast) if demand_forecast else 0
        if peak_demand > 15:
            recommendations.append({
                "type": "staffing",
                "message": f"Peak demand of {peak_demand} appointments expected. Consider adding more doctors.",
                "priority": "High"
            })
        
        if total_appointments < 50:
            recommendations.append({
                "type": "data",
                "message": f"Only {total_appointments} appointments recorded. Continue collecting data for better predictions.",
                "priority": "Medium"
            })
        
        if not recommendations:
            recommendations.append({
                "type": "normal",
                "message": "All metrics are normal. Continue standard operations.",
                "priority": "Low"
            })
        
        return jsonify({
            "demand_forecast": {
                "next_7_days": demand_forecast,
                "dates": dates,
                "current_bookings": daily_bookings,
                "total_forecast": sum(demand_forecast),
                "average_daily": sum(demand_forecast) / 7 if demand_forecast else 0
            },
            "risk_analysis": {
                "high_risk_count": len(high_risk_appointments),
                "medium_risk_count": len(medium_risk_appointments),
                "low_risk_count": len(low_risk_appointments),
                "high_risk_appointments": high_risk_appointments,
                "historical_no_show_rate": round(no_show_rate, 1)
            },
            "recommendations": recommendations,
            "model_status": {
                "no_show_model": appointment_predictor is not None and appointment_predictor.model is not None,
                "demand_model": demand_predictor is not None and demand_predictor.model is not None,
                "no_show_accuracy": "85%",  # Placeholder
                "demand_accuracy": "78%"     # Placeholder
            },
            "total_appointments": total_appointments,
            "total_patients": total_patients,
            "total_doctors": total_doctors
        }), 200
        
    except Exception as e:
        print(f"Error in ml_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def generate_recommendations(self, demand_forecast, high_risk_appointments):
    """Generate actionable recommendations"""
    recommendations = []
    
    # Check for high demand days
    high_demand_days = [i for i, d in enumerate(demand_forecast) if d > 15]
    if high_demand_days:
        recommendations.append({
            "type": "staffing",
            "message": f"High demand expected in next {len(high_demand_days)} days. Consider adding more doctors.",
            "priority": "High"
        })
    
    # Check for no-show risks
    if len(high_risk_appointments) > 3:
        recommendations.append({
            "type": "reminder",
            "message": f"{len(high_risk_appointments)} appointments have high no-show risk. Send reminders.",
            "priority": "Medium"
        })
    
    # Resource optimization
    if max(demand_forecast) > 20:
        recommendations.append({
            "type": "capacity",
            "message": "Peak load expected. Consider extending operating hours.",
            "priority": "High"
        })
    
    if not recommendations:
        recommendations.append({
            "type": "normal",
            "message": "All metrics are normal. Continue standard operations.",
            "priority": "Low"
        })
    
    return recommendations


# Add this to ml_dashboard.py

@ml_bp.route("/train", methods=["POST"])
@jwt_required()
def train_models():
    """Train ML models"""
    try:
        from ml_models import train_all_models
        train_all_models()
        
        return jsonify({
            "message": "Models trained successfully!",
            "status": "success"
        }), 200
    except Exception as e:
        return jsonify({
            "message": f"Training error: {str(e)}",
            "status": "error"
        }), 500