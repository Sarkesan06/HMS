from app import mongo, mail
from datetime import datetime, timedelta
from flask_mail import Message

def send_appointment_reminder(to_email, patient_name, doctor_name, appointment_date, appointment_time, appointment_id, consult_type):
    """Send appointment reminder email"""
    
    # Format date
    date_obj = datetime.strptime(appointment_date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%A, %B %d, %Y')
    
    # Build email content
    subject = f"🔔 Appointment Reminder: Dr. {doctor_name} on {formatted_date}"
    
    if consult_type == "online":
        body = f"""
Hospital Management System - Appointment Reminder

Dear {patient_name},

This is a reminder for your upcoming ONLINE consultation with Dr. {doctor_name}.

Appointment Details:
📅 Date: {formatted_date}
🕐 Time: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor_name}
🆔 Appointment ID: {appointment_id}

To join the video consultation:
1. Go to the Consultation page in the HMS portal
2. Enter your Appointment ID: {appointment_id}
3. Click "Start / Join Call"

OR use this direct link:
https://meet.jit.si/HMS_{appointment_id}

Please join 5 minutes before your scheduled time.

Important:
- Ensure you have a stable internet connection
- Allow camera and microphone access
- Find a quiet, well-lit location

Thank you for choosing our hospital!
"""
    else:
        body = f"""
Hospital Management System - Appointment Reminder

Dear {patient_name},

This is a reminder for your upcoming IN-PERSON consultation with Dr. {doctor_name}.

Appointment Details:
📅 Date: {formatted_date}
🕐 Time: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor_name}
🆔 Appointment ID: {appointment_id}

Please bring:
- Any relevant medical reports
- Valid ID proof
- Insurance card (if applicable)

Please arrive 10 minutes before your scheduled time.

Thank you for choosing our hospital!
"""
    
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender='sharkroshan@gmail.com'  # Explicitly set sender
        )
        mail.send(msg)
        print(f"✅ Reminder sent for appointment {appointment_id} to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False

def check_and_send_reminders():
    """Check for appointments in the next 5 minutes and send reminders"""
    
    try:
        # Get current time
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M')
        
        # Calculate 5 minutes from now
        future_time = (now + timedelta(minutes=5)).strftime('%H:%M')
        
        print(f"🔍 Checking appointments between {current_time} and {future_time} on {current_date}")
        
        # Find appointments in the next 5 minutes
        appointments = mongo.db.appointments.find({
            "date": current_date,
            "time": {"$gte": current_time, "$lte": future_time},
            "status": "Pending",
            "reminder_sent": {"$ne": True}
        })
        
        # Convert to list to count
        appointments_list = list(appointments)
        print(f"📊 Found {len(appointments_list)} appointments to check")
        
        reminders_sent = 0
        
        for appointment in appointments_list:
            print(f"📧 Processing appointment: {appointment.get('_id')}")
            print(f"   Time: {appointment.get('time')}, Status: {appointment.get('status')}")
            
            # Get patient email
            patient_email = None
            patient_name = appointment.get('patient', 'Patient')
            
            # Try to get patient email from patients collection
            patient_id = appointment.get('patient_id')
            if patient_id:
                from bson.objectid import ObjectId
                try:
                    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
                    if patient:
                        patient_email = patient.get('email')
                        patient_name = patient.get('name', patient_name)
                        print(f"   Found patient email from patients collection: {patient_email}")
                except Exception as e:
                    print(f"   Error finding patient: {e}")
            
            # Also check if email was provided in appointment
            if not patient_email:
                patient_email = appointment.get('patient_email')
                if patient_email:
                    print(f"   Found patient email from appointment: {patient_email}")
            
            if patient_email:
                print(f"   Sending reminder to: {patient_email}")
                # Send reminder email
                success = send_appointment_reminder(
                    to_email=patient_email,
                    patient_name=patient_name,
                    doctor_name=appointment.get('doctor', 'Doctor'),
                    appointment_date=appointment.get('date'),
                    appointment_time=appointment.get('time'),
                    appointment_id=str(appointment.get('_id')),
                    consult_type=appointment.get('type', 'offline')
                )
                
                if success:
                    # Mark reminder as sent
                    mongo.db.appointments.update_one(
                        {"_id": appointment.get('_id')},
                        {"$set": {"reminder_sent": True, "reminder_sent_at": datetime.now()}}
                    )
                    reminders_sent += 1
                    print(f"   ✅ Reminder sent and marked as sent")
            else:
                print(f"   ⚠️ No email found for patient in appointment {appointment.get('_id')}")
        
        if reminders_sent > 0:
            print(f"✅ Sent {reminders_sent} appointment reminders")
        else:
            print("📭 No appointments found for reminder in the next 5 minutes")
            
    except Exception as e:
        print(f"❌ Error in check_and_send_reminders: {str(e)}")
        import traceback
