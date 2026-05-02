# train_models.py
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from ml_models import train_all_models

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        print("\n" + "="*60)
        print("🤖 Starting ML Model Training")
        print("="*60)
        
        # Check if we have enough data
        from app import mongo
        total_appointments = mongo.db.appointments.count_documents({})
        
        print(f"\n📊 Total appointments in database: {total_appointments}")
        
        if total_appointments < 50:
            print(f"\n⚠️ Need at least 50 appointments for training.")
            print(f"   Currently have: {total_appointments}")
            print(f"   Need: {50 - total_appointments} more appointments")
            print("\n💡 Tip: Create more appointments through the dashboard first.")
        else:
            train_all_models()
        
        print("\n" + "="*60)