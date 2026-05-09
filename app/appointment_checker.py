from datetime import datetime, timedelta

from app import mongo
from app.email_utils import send_email


def send_appointment_reminder(to_email, patient_name, doctor_name, appointment_date, appointment_time, appointment_id, consult_type):
    """Send appointment reminder email."""

    date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%A, %B %d, %Y")
    subject = f"Appointment Reminder: Dr. {doctor_name} on {formatted_date}"

    if consult_type == "online":
        join_link = f"https://meet.jit.si/HMS_{appointment_id}"
        text_body = f"""
Hospital Management System - Appointment Reminder

Dear {patient_name},

This is a reminder for your upcoming ONLINE consultation with Dr. {doctor_name}.

Appointment Details:
Date: {formatted_date}
Time: {appointment_time}
Doctor: Dr. {doctor_name}
Appointment ID: {appointment_id}

To join the video consultation:
1. Go to the Consultation page in the HMS portal
2. Enter your Appointment ID: {appointment_id}
3. Click "Start / Join Call"

OR use this direct link:
{join_link}

Please join 5 minutes before your scheduled time.

Important:
- Ensure you have a stable internet connection
- Allow camera and microphone access
- Find a quiet, well-lit location

Thank you for choosing our hospital!
"""

        html_body = f"""
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
    <h2>Hospital Management System</h2>
    <p><strong>Appointment Reminder</strong></p>
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>This is a reminder for your upcoming <strong>ONLINE</strong> consultation with Dr. {doctor_name}.</p>
    <p><strong>Appointment Details</strong><br>
      Date: {formatted_date}<br>
      Time: {appointment_time}<br>
      Doctor: Dr. {doctor_name}<br>
      Appointment ID: {appointment_id}
    </p>
    <p><strong>To join the video consultation:</strong><br>
      1. Go to the Consultation page in the HMS portal<br>
      2. Enter Appointment ID: {appointment_id}<br>
      3. Click "Start / Join Call"
    </p>
    <p>Direct link: <a href="{join_link}">{join_link}</a></p>
    <p>Please join 5 minutes before your scheduled time.</p>
  </body>
</html>
"""
    else:
        text_body = f"""
Hospital Management System - Appointment Reminder

Dear {patient_name},

This is a reminder for your upcoming IN-PERSON consultation with Dr. {doctor_name}.

Appointment Details:
Date: {formatted_date}
Time: {appointment_time}
Doctor: Dr. {doctor_name}
Appointment ID: {appointment_id}

Please bring relevant medical documents and arrive 10 minutes early.

Thank you for choosing our hospital!
"""

        html_body = f"""
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
    <h2>Hospital Management System</h2>
    <p><strong>Appointment Reminder</strong></p>
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>This is a reminder for your upcoming <strong>IN-PERSON</strong> consultation with Dr. {doctor_name}.</p>
    <p><strong>Appointment Details</strong><br>
      Date: {formatted_date}<br>
      Time: {appointment_time}<br>
      Doctor: Dr. {doctor_name}<br>
      Appointment ID: {appointment_id}
    </p>
    <p>Please bring relevant medical documents and arrive 10 minutes early.</p>
  </body>
</html>
"""

    success = send_email(to_email, subject, text_body, html_body)
    if success:
        print(f"Reminder sent for appointment {appointment_id} to {to_email}")
    else:
        print(f"Reminder email failed for appointment {appointment_id} to {to_email}")
    return success


def check_and_send_reminders():
    """Check for appointments in the next 5 minutes and send reminders."""

    try:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        future_time = (now + timedelta(minutes=5)).strftime("%H:%M")

        print(f"Checking appointments between {current_time} and {future_time} on {current_date}")

        appointments = mongo.db.appointments.find({
            "date": current_date,
            "time": {"$gte": current_time, "$lte": future_time},
            "status": "Pending",
            "reminder_sent": {"$ne": True},
        })

        appointments_list = list(appointments)
        print(f"Found {len(appointments_list)} appointments to check")

        reminders_sent = 0

        for appointment in appointments_list:
            patient_email = None
            patient_name = appointment.get("patient", "Patient")

            patient_id = appointment.get("patient_id")
            if patient_id:
                from bson.objectid import ObjectId

                try:
                    patient = mongo.db.patients.find_one({"_id": ObjectId(patient_id)})
                    if patient:
                        patient_email = patient.get("email")
                        patient_name = patient.get("name", patient_name)
                except Exception as exc:
                    print(f"Error finding patient: {exc}")

            if not patient_email:
                patient_email = appointment.get("patient_email")

            if patient_email:
                success = send_appointment_reminder(
                    to_email=patient_email,
                    patient_name=patient_name,
                    doctor_name=appointment.get("doctor", "Doctor"),
                    appointment_date=appointment.get("date"),
                    appointment_time=appointment.get("time"),
                    appointment_id=str(appointment.get("_id")),
                    consult_type=appointment.get("type", "offline"),
                )

                if success:
                    mongo.db.appointments.update_one(
                        {"_id": appointment.get("_id")},
                        {"$set": {"reminder_sent": True, "reminder_sent_at": datetime.now()}},
                    )
                    reminders_sent += 1

        if reminders_sent > 0:
            print(f"Sent {reminders_sent} appointment reminders")
        else:
            print("No appointments found for reminder in the next 5 minutes")

    except Exception as exc:
        print(f"Error in check_and_send_reminders: {exc}")
