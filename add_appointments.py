# fix_appointments.py
from app import create_app, mongo
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("\n" + "="*50)
    print("FIXING APPOINTMENT DATA")
    print("="*50)
    
    # Check current appointments
    all_appointments = list(mongo.db.appointments.find({}))
    print(f"\n📊 Found {len(all_appointments)} total appointments")
    
    if len(all_appointments) == 0:
        print("\n⚠️ No appointments found! Creating sample appointments...")
        
        # Get doctors and patients
        doctors = list(mongo.db.doctors.find({}))
        patients = list(mongo.db.patients.find({}))
        
        if not doctors:
            print("❌ No doctors found. Please add doctors first.")
            exit()
        if not patients:
            print("❌ No patients found. Please add patients first.")
            exit()
        
        # Create 30 sample appointments with proper statuses
        statuses = ['Pending', 'Completed', 'Cancelled']
        status_weights = [0.5, 0.3, 0.2]  # 50% pending, 30% completed, 20% cancelled
        
        for i in range(50):
            status = random.choices(statuses, weights=status_weights)[0]
            future_date = datetime.now() + timedelta(days=random.randint(-10, 20))
            
            appointment = {
                "doctor": doctors[i % len(doctors)].get("name", "Dr. Smith"),
                "doctor_id": str(doctors[i % len(doctors)]["_id"]),
                "patient": patients[i % len(patients)].get("name", "Test Patient"),
                "patient_id": str(patients[i % len(patients)]["_id"]),
                "date": future_date.strftime('%Y-%m-%d'),
                "time": f"{random.randint(9, 16)}:00",
                "status": status,
                "priority": random.choice(['Normal', 'Emergency']),
                "type": random.choice(['offline', 'online']),
                "created_at": datetime.utcnow()
            }
            mongo.db.appointments.insert_one(appointment)
            print(f"✅ Added: {appointment['date']} - {status}")
    
    else:
        # Update existing appointments to have proper statuses if they're missing
        print("\n🔄 Updating existing appointments...")
        for appt in all_appointments:
            if not appt.get('status') or appt.get('status') == '':
                # Assign a random status
                status = random.choice(['Pending', 'Completed', 'Cancelled'])
                mongo.db.appointments.update_one(
                    {"_id": appt["_id"]},
                    {"$set": {"status": status}}
                )
                print(f"✅ Updated appointment {appt.get('patient')} to status: {status}")
    
    # Show final counts
    pending = mongo.db.appointments.count_documents({"status": "Pending"})
    completed = mongo.db.appointments.count_documents({"status": "Completed"})
    cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
    total = mongo.db.appointments.count_documents({})
    
    print("\n" + "="*50)
    print("FINAL STATUS COUNTS:")
    print(f"📊 Total: {total}")
    print(f"⏳ Pending: {pending}")
    print(f"✅ Completed: {completed}")
    print(f"❌ Cancelled: {cancelled}")
    print("="*50)