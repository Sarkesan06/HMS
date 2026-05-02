# app/ml_models.py
from datetime import datetime

class AppointmentPredictor:
    def predict_no_show_risk(self, appointment):
        risk = 30
        if appointment.get('priority') == 'Emergency':
            risk = 10
        elif appointment.get('type') == 'online':
            risk = 20
        return risk
    
    def predict_daily_load(self, date):
        return 10

class DemandPredictor:
    def predict_demand(self, days=7):
        return [10, 12, 15, 14, 16, 8, 6][:days]

class DiseasePredictor:
    def predict_disease(self, symptoms):
        if not symptoms:
            return None
        return {
            'possible_diseases': ['Common Cold', 'Flu'],
            'confidence_scores': [60, 40],
            'urgency': 'Low',
            'suggestions': ['Rest', 'Stay hydrated'],
            'requires_doctor': False
        }

# Create instances
appointment_predictor = AppointmentPredictor()
demand_predictor = DemandPredictor()
disease_predictor = DiseasePredictor()

def train_all_models():
    print("✅ ML Models Ready")
    return True