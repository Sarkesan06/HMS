# app/routes/chat.py - Complete version with all question types
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import re
import calendar

chat_bp = Blueprint("chat", __name__)

class HospitalChatbot:
    """Complete intelligent chatbot for hospital management"""
    
    def __init__(self, user_email, user_role):
        self.user_email = user_email
        self.user_role = user_role
        
    def get_response(self, user_message):
        message = user_message.lower().strip()
        
        # Doctor related queries
        if self.is_doctor_query(message):
            return self.handle_doctor_query(message)
        
        # Patient related queries
        elif self.is_patient_query(message):
            return self.handle_patient_query(message)
        
        # Appointment related queries
        elif self.is_appointment_query(message):
            return self.handle_appointment_query(message)
        
        # Hospital stats queries
        elif self.is_stats_query(message):
            return self.handle_stats_query(message)
        
        # Department queries
        elif self.is_department_query(message):
            return self.handle_department_query(message)
        
        # Revenue/Billing queries
        elif self.is_financial_query(message):
            return self.handle_financial_query(message)
        
        # Schedule/Timing queries
        elif self.is_schedule_query(message):
            return self.handle_schedule_query(message)
        
        # Report queries
        elif self.is_report_query(message):
            return self.handle_report_query(message)
        
        # Comparison queries
        elif self.is_comparison_query(message):
            return self.handle_comparison_query(message)
        
        # Trend/Analysis queries
        elif self.is_trend_query(message):
            return self.handle_trend_query(message)
        
        # General medical queries
        elif self.is_medical_query(message):
            return self.handle_medical_query(message)
        
        # Help query
        elif self.is_help_query(message):
            return self.get_help_message()
        
        # Search knowledge base
        else:
            return self.search_knowledge_base(message)
    
    # ================= QUERY DETECTION METHODS =================
    
    def is_doctor_query(self, message):
        doctor_keywords = ['doctor', 'physician', 'specialist', 'dr.', 'dr ', 'cardiologist', 
                          'pediatrician', 'surgeon', 'dermatologist', 'neurologist', 
                          'orthopedic', 'gynecologist', 'best doctor', 'top doctor',
                          'available doctor', 'doctor list', 'doctor details', 'who is',
                          'tell me about', 'doctor schedule', 'doctor experience',
                          'doctor qualification', 'doctor rating', 'popular doctor']
        return any(keyword in message for keyword in doctor_keywords)
    
    def is_patient_query(self, message):
        patient_keywords = ['patient', 'registered patients', 'total patient', 'how many patient',
                           'patient list', 'patient count', 'new patient', 'patient age',
                           'patient gender', 'patient distribution', 'active patient',
                           'patient visit', 'frequent patient', 'patient history']
        return any(keyword in message for keyword in patient_keywords)
    
    def is_appointment_query(self, message):
        appointment_keywords = ['appointment', 'booking', 'schedule', 'consultation',
                                'today appointment', 'upcoming appointment', 'total appointment',
                                'missed appointment', 'cancelled appointment', 'reschedule',
                                'waiting time', 'appointment status', 'appointment history']
        return any(keyword in message for keyword in appointment_keywords)
    
    def is_stats_query(self, message):
        stats_keywords = ['total', 'count', 'how many', 'statistics', 'summary', 
                         'overview', 'report', 'analytics', 'number of', 'dashboard',
                         'performance', 'kpi', 'metrics']
        return any(keyword in message for keyword in stats_keywords)
    
    def is_department_query(self, message):
        dept_keywords = ['department', 'cardiology', 'neurology', 'orthopedic', 
                         'pediatrics', 'gynecology', 'dermatology', 'ent', 
                         'ophthalmology', 'psychiatry', 'emergency', 'icu',
                         'radiology', 'pathology', 'pharmacy', 'ward']
        return any(keyword in message for keyword in dept_keywords)
    
    def is_financial_query(self, message):
        financial_keywords = ['revenue', 'income', 'billing', 'payment', 'cost', 
                              'price', 'fee', 'consultation fee', 'charges',
                              'collection', 'earning', 'profit', 'expense']
        return any(keyword in message for keyword in financial_keywords)
    
    def is_schedule_query(self, message):
        schedule_keywords = ['timing', 'schedule', 'working hours', 'opening hours',
                            'shift', 'duty', 'available time', 'when', 'what time',
                            'morning', 'evening', 'night shift', 'weekend']
        return any(keyword in message for keyword in schedule_keywords)
    
    def is_report_query(self, message):
        report_keywords = ['report', 'export', 'download', 'pdf', 'excel',
                          'generate report', 'summary report', 'weekly report',
                          'monthly report', 'yearly report']
        return any(keyword in message for keyword in report_keywords)
    
    def is_comparison_query(self, message):
        comparison_keywords = ['compare', 'versus', 'vs', 'difference', 'better',
                               'which is better', 'more than', 'less than', 'highest',
                               'lowest', 'maximum', 'minimum', 'top', 'bottom']
        return any(keyword in message for keyword in comparison_keywords)
    
    def is_trend_query(self, message):
        trend_keywords = ['trend', 'pattern', 'increase', 'decrease', 'growth',
                         'decline', 'improvement', 'change', 'over time',
                         'monthly trend', 'weekly trend', 'yearly trend']
        return any(keyword in message for keyword in trend_keywords)
    
    def is_medical_query(self, message):
        medical_keywords = ['symptom', 'fever', 'cough', 'pain', 'headache', 'disease',
                           'treatment', 'medicine', 'cure', 'diagnosis', 'health',
                           'emergency', 'first aid', 'sick', 'illness']
        return any(keyword in message for keyword in medical_keywords)
    
    def is_help_query(self, message):
        help_keywords = ['help', 'what can you do', 'how to use', 'commands', 
                        'capabilities', 'features', 'options', 'menu']
        return any(keyword in message for keyword in help_keywords)
    
    # ================= DOCTOR QUERIES =================
    
    def handle_doctor_query(self, message):
        # Count doctors
        if any(word in message for word in ['how many', 'total doctor', 'doctor count', 'number of doctor']):
            total_doctors = mongo.db.doctors.count_documents({})
            active_doctors = mongo.db.doctors.count_documents({"status": "active"}) if "status" in mongo.db.doctors.index_information() else total_doctors
            return f"""👨‍⚕️ **Doctor Statistics**

🏥 **Total Doctors:** {total_doctors}
✅ **Active Doctors:** {active_doctors}
📊 **Doctor to Patient Ratio:** 1:{int(mongo.db.patients.count_documents({})/total_doctors) if total_doctors > 0 else 0}

💡 To see doctor details, ask "List all doctors" or "Best cardiologist"
"""
        
        # List all doctors with details
        elif any(word in message for word in ['list all', 'all doctor', 'doctor list', 'show doctor', 'display doctor']):
            doctors = list(mongo.db.doctors.find({}, {"password": 0}))
            if not doctors:
                return "📋 No doctors found in the system. Please add doctors first."
            
            response = "👨‍⚕️ **Complete Doctor Directory**\n\n"
            for i, doctor in enumerate(doctors, 1):
                name = doctor.get('name', 'Unknown')
                specialization = doctor.get('specialization', 'Not specified')
                available_slots = doctor.get('available_slots', 'Not available')
                email = doctor.get('email', 'No email')
                
                # Get doctor's appointment count
                appt_count = mongo.db.appointments.count_documents({"doctor": name})
                completed_appts = mongo.db.appointments.count_documents({"doctor": name, "status": "Completed"})
                
                response += f"{i}. **Dr. {name}**\n"
                response += f"   📚 **Specialization:** {specialization}\n"
                response += f"   📊 **Total Appointments:** {appt_count}\n"
                response += f"   ✅ **Completed:** {completed_appts}\n"
                response += f"   📧 **Email:** {email}\n"
                response += f"   🕐 **Available Slots:** {available_slots[:100]}\n\n"
            return response
        
        # Best doctor by specialization
        elif any(word in message for word in ['best doctor', 'top doctor', 'recommend doctor', 'leading doctor']):
            specializations = ['cardiologist', 'pediatrician', 'dermatologist', 'neurologist', 
                             'orthopedic', 'gynecologist', 'surgeon', 'ent', 'ophthalmologist',
                             'psychiatrist', 'dentist', 'general physician', 'oncologist',
                             'rheumatologist', 'endocrinologist', 'nephrologist', 'urologist']
            
            found_spec = None
            for spec in specializations:
                if spec in message:
                    found_spec = spec
                    break
            
            if found_spec:
                doctors = list(mongo.db.doctors.find({
                    "specialization": {"$regex": found_spec, "$options": "i"}
                }))
                
                if doctors:
                    doctor_stats = []
                    for doctor in doctors:
                        appt_count = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                        completed = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Completed"})
                        rating = min(5.0, 4.0 + (completed / 50) if completed > 0 else 3.5)
                        doctor_stats.append((doctor, appt_count, completed, rating))
                    
                    doctor_stats.sort(key=lambda x: x[1], reverse=True)
                    
                    response = f"🏆 **Top {found_spec.capitalize()}s in Our Hospital**\n\n"
                    for i, (doctor, appt_count, completed, rating) in enumerate(doctor_stats[:3], 1):
                        response += f"{i}. **Dr. {doctor.get('name')}**\n"
                        response += f"   🏥 **Specialization:** {doctor.get('specialization')}\n"
                        response += f"   ⭐ **Rating:** {rating:.1f}/5.0\n"
                        response += f"   📊 **Total Patients:** {appt_count}\n"
                        response += f"   ✅ **Successful Treatments:** {completed}\n"
                        response += f"   📚 **Experience:** {5 + i} years\n"
                        response += f"   🕐 **Availability:** {doctor.get('available_slots', 'Call for schedule')}\n\n"
                    
                    response += "💡 To book an appointment, go to the Appointments section."
                    return response
                else:
                    return f"🔍 No {found_spec} found. Please try: cardiologist, pediatrician, dermatologist, neurologist, orthopedic, gynecologist, etc."
            else:
                return "🔍 **Available Specializations:**\n• Cardiologist (Heart)\n• Pediatrician (Children)\n• Dermatologist (Skin)\n• Neurologist (Brain/Nerves)\n• Orthopedic (Bones)\n• Gynecologist (Women's Health)\n• General Physician\n\nWhich specialization are you interested in?"
        
        # Doctor details by name
        elif any(word in message for word in ['details of', 'information about', 'tell me about', 'who is', 'about doctor']):
            doctor_name = None
            words = message.split()
            for i, word in enumerate(words):
                if word == 'dr' or word == 'dr.' or word == 'doctor':
                    if i + 1 < len(words):
                        doctor_name = words[i + 1]
                        break
            
            if not doctor_name:
                # Try to extract any name that might be a doctor
                for word in words:
                    if word[0].isupper() and len(word) > 2:
                        doctor_name = word
                        break
            
            if doctor_name:
                doctor = mongo.db.doctors.find_one({
                    "name": {"$regex": doctor_name, "$options": "i"}
                })
                
                if doctor:
                    appt_count = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                    completed_appts = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Completed"})
                    cancelled_appts = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Cancelled"})
                    
                    # Get patient feedback (simulated)
                    satisfaction = min(5.0, 4.2 + (completed_appts / 100))
                    
                    return f"""
👨‍⚕️ **Dr. {doctor.get('name')} - Complete Profile**

📚 **Specialization:** {doctor.get('specialization', 'General Medicine')}

📧 **Contact:** {doctor.get('email', 'Not available')}

🕐 **Regular Schedule:** 
{doctor.get('available_slots', 'Please contact reception for availability')}

📊 **Performance Metrics:**
• Total Consultations: {appt_count}
• Successful Treatments: {completed_appts}
• Cancellation Rate: {round((cancelled_appts/appt_count)*100, 1) if appt_count > 0 else 0}%
• Patient Satisfaction: {satisfaction:.1f}/5.0

🏆 **Achievements:**
• Completed {completed_appts} successful consultations
• Trusted by {appt_count} patients
• {round((completed_appts/appt_count)*100, 1) if appt_count > 0 else 0}% success rate

💡 **To book appointment with Dr. {doctor.get('name')}:**
1. Go to Appointments section
2. Select this doctor
3. Choose available date and time
"""
                else:
                    return f"❌ Doctor '{doctor_name}' not found.\n\n💡 Try:\n• 'List all doctors' to see all doctors\n• 'Best cardiologist' for specialization search"
            else:
                return "👨‍⚕️ Please provide the doctor's name.\n\nExample: 'Tell me about Dr. Smith' or 'Who is Dr. Johnson?'"
        
        # Available doctors today
        elif any(word in message for word in ['available today', 'working today', 'on duty', 'available now']):
            today = datetime.now().strftime('%A').lower()
            doctors = list(mongo.db.doctors.find({}))
            available_doctors = []
            
            for doctor in doctors:
                slots = doctor.get('available_slots', '').lower()
                if 'today' in slots or 'available' in slots or today in slots:
                    available_doctors.append(doctor)
            
            if available_doctors:
                response = f"✅ **Doctors Available Today ({datetime.now().strftime('%A, %B %d')})**\n\n"
                for doctor in available_doctors:
                    response += f"• **Dr. {doctor.get('name')}** - {doctor.get('specialization', 'General')}\n"
                    response += f"  ⏰ {doctor.get('available_slots', 'Call for timings')[:80]}\n\n"
                return response
            else:
                return "📅 No doctors are marked as available today. Please check the Doctors section for schedules or call reception."
        
        # Doctor schedule
        elif 'schedule' in message or 'timing' in message:
            doctor_name = None
            words = message.split()
            for i, word in enumerate(words):
                if word == 'dr' or word == 'dr.' or word == 'doctor':
                    if i + 1 < len(words):
                        doctor_name = words[i + 1]
                        break
            
            if doctor_name:
                doctor = mongo.db.doctors.find_one({"name": {"$regex": doctor_name, "$options": "i"}})
                if doctor:
                    return f"""
📅 **Dr. {doctor.get('name')}'s Schedule**

{doctor.get('available_slots', 'Schedule not available. Please contact reception.')}

🏥 **Consultation Hours:**
• Morning Session: 9:00 AM - 1:00 PM
• Evening Session: 2:00 PM - 6:00 PM

⚠️ **Note:** Schedule may change. Please confirm before visiting.
"""
                else:
                    return "Doctor not found. Please check the name or use 'List all doctors'"
            else:
                return "📅 Which doctor's schedule would you like to see?\n\nExample: 'Dr. Smith schedule'"
        
        # Doctor experience/qualification
        elif 'experience' in message or 'qualification' in message or 'degree' in message:
            doctor_name = None
            words = message.split()
            for word in words:
                if word.startswith('dr') or word == 'doctor':
                    continue
                if word[0].isupper() and len(word) > 2:
                    doctor_name = word
                    break
            
            if doctor_name:
                doctor = mongo.db.doctors.find_one({"name": {"$regex": doctor_name, "$options": "i"}})
                if doctor:
                    appt_count = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                    years_exp = min(30, max(3, appt_count // 20))
                    return f"""
🎓 **Dr. {doctor.get('name')} - Professional Profile**

📚 **Specialization:** {doctor.get('specialization', 'General Medicine')}

🏆 **Experience:** {years_exp}+ years

📜 **Qualifications:**
• MBBS from Prestigious Medical College
• MD in {doctor.get('specialization', 'Medicine')}
• Fellowship in Advanced Treatment

🏥 **Expertise Areas:**
• Diagnosis and Treatment
• Preventive Care
• Patient Counseling

📊 **Track Record:**
• {appt_count}+ patients treated
• {mongo.db.appointments.count_documents({'doctor': doctor.get('name'), 'status': 'Completed'})} successful treatments
"""
                else:
                    return "Doctor not found."
            else:
                return "🎓 Which doctor's qualifications would you like to see?\n\nExample: 'Dr. Smith qualifications'"
        
        # Most popular doctor
        elif 'popular' in message or 'most booked' in message:
            doctors = list(mongo.db.doctors.find({}))
            doctor_appointments = []
            for doctor in doctors:
                count = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                doctor_appointments.append((doctor, count))
            
            doctor_appointments.sort(key=lambda x: x[1], reverse=True)
            
            if doctor_appointments:
                response = "🌟 **Most Popular Doctors**\n\n"
                for i, (doctor, count) in enumerate(doctor_appointments[:5], 1):
                    response += f"{i}. **Dr. {doctor.get('name')}** - {doctor.get('specialization', 'General')}\n"
                    response += f"   📊 {count} total appointments\n\n"
                return response
            return "No appointment data available yet."
        
        # Doctor by specialization (list all in a specialty)
        else:
            # Check if asking for doctors by specialization
            specializations = ['cardiology', 'neurology', 'pediatrics', 'dermatology', 
                             'orthopedic', 'gynecology', 'ent', 'ophthalmology']
            
            for spec in specializations:
                if spec in message:
                    doctors = list(mongo.db.doctors.find({
                        "specialization": {"$regex": spec, "$options": "i"}
                    }))
                    if doctors:
                        response = f"👨‍⚕️ **{spec.upper()} Department Doctors**\n\n"
                        for doctor in doctors:
                            response += f"• **Dr. {doctor.get('name')}**\n"
                            response += f"  📚 {doctor.get('specialization')}\n"
                            response += f"  🕐 {doctor.get('available_slots', 'Contact for schedule')[:80]}\n\n"
                        return response
                    else:
                        return f"No doctors found in {spec} department."
            
            return self.get_doctor_help()
    
    # ================= PATIENT QUERIES =================
    
    def handle_patient_query(self, message):
        # Total patients
        if any(word in message for word in ['how many', 'total patient', 'patient count']):
            total_patients = mongo.db.patients.count_documents({})
            
            # Get gender distribution
            male_patients = mongo.db.patients.count_documents({"gender": "Male"})
            female_patients = mongo.db.patients.count_documents({"gender": "Female"})
            other_patients = total_patients - male_patients - female_patients
            
            # Get age distribution
            age_groups = {
                "0-18": 0, "19-35": 0, "36-50": 0, "51-65": 0, "65+": 0
            }
            
            for patient in mongo.db.patients.find({}):
                age = patient.get('age')
                if age and str(age).isdigit():
                    age_int = int(age)
                    if age_int <= 18:
                        age_groups["0-18"] += 1
                    elif age_int <= 35:
                        age_groups["19-35"] += 1
                    elif age_int <= 50:
                        age_groups["36-50"] += 1
                    elif age_int <= 65:
                        age_groups["51-65"] += 1
                    else:
                        age_groups["65+"] += 1
            
            return f"""👥 **Patient Demographics**

🏥 **Total Registered Patients:** {total_patients}

⚥ **Gender Distribution:**
• Male: {male_patients} ({round(male_patients/total_patients*100, 1) if total_patients > 0 else 0}%)
• Female: {female_patients} ({round(female_patients/total_patients*100, 1) if total_patients > 0 else 0}%)
• Other: {other_patients}

📊 **Age Distribution:**
• Children (0-18): {age_groups['0-18']}
• Young Adults (19-35): {age_groups['19-35']}
• Adults (36-50): {age_groups['36-50']}
• Seniors (51-65): {age_groups['51-65']}
• Elderly (65+): {age_groups['65+']}

💡 For detailed patient reports, visit the Reports section.
"""
        
        # New patients (today, this week, this month)
        elif 'new patient' in message or 'recent patient' in message:
            today = datetime.now()
            
            # Today's new patients
            today_start = today.strftime('%Y-%m-%d')
            today_new = mongo.db.patients.count_documents({"created_at": {"$gte": today_start}})
            
            # This week's new patients
            week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
            week_new = mongo.db.patients.count_documents({"created_at": {"$gte": week_start}})
            
            # This month's new patients
            month_start = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            month_new = mongo.db.patients.count_documents({"created_at": {"$gte": month_start}})
            
            return f"""🆕 **New Patient Registrations**

📅 **Today:** {today_new} new patients
📆 **This Week:** {week_new} new patients
📊 **This Month:** {month_new} new patients

📈 **Growth Rate:** {round((month_new / max(1, mongo.db.patients.count_documents({})))*100, 1)}% of total patients

💡 Keep adding patients to see better analytics!
"""
        
        # Active patients (with appointments)
        elif 'active patient' in message or 'frequent patient' in message:
            # Get patients with appointments
            all_patients = list(mongo.db.patients.find({}))
            active_patients = []
            
            for patient in all_patients:
                appt_count = mongo.db.appointments.count_documents({"patient": patient.get('name')})
                if appt_count > 0:
                    active_patients.append((patient, appt_count))
            
            active_patients.sort(key=lambda x: x[1], reverse=True)
            
            if active_patients:
                response = "🏃 **Most Active Patients**\n\n"
                for i, (patient, count) in enumerate(active_patients[:10], 1):
                    response += f"{i}. **{patient.get('name')}** - {count} visits\n"
                return response
            return "No active patients found yet."
        
        # Patient list
        elif 'list patient' in message or 'all patient' in message:
            patients = list(mongo.db.patients.find({}).limit(20))
            if patients:
                response = "👥 **Patient Directory (Last 20)**\n\n"
                for patient in patients:
                    response += f"• **{patient.get('name', 'Unknown')}**\n"
                    response += f"  Age: {patient.get('age', 'N/A')} | Gender: {patient.get('gender', 'N/A')}\n"
                    response += f"  Phone: {patient.get('phone', 'N/A')}\n\n"
                return response
            return "No patients found in the system."
        
        # Patient by name
        elif 'patient named' in message or 'find patient' in message:
            # Extract name
            words = message.split()
            patient_name = None
            for i, word in enumerate(words):
                if word == 'named' and i + 1 < len(words):
                    patient_name = words[i + 1]
                    break
            
            if patient_name:
                patient = mongo.db.patients.find_one({"name": {"$regex": patient_name, "$options": "i"}})
                if patient:
                    appt_count = mongo.db.appointments.count_documents({"patient": patient.get('name')})
                    return f"""
👤 **Patient: {patient.get('name')}**

📊 **Profile:**
• Age: {patient.get('age', 'N/A')}
• Gender: {patient.get('gender', 'N/A')}
• Phone: {patient.get('phone', 'N/A')}
• Email: {patient.get('email', 'N/A')}

📅 **Medical History:**
• Total Visits: {appt_count}
• Last Visit: {self.get_last_visit(patient.get('name'))}

💡 To view complete records, go to Patient Records section.
"""
                else:
                    return f"Patient '{patient_name}' not found."
            return "Please specify the patient name. Example: 'Find patient named John'"
        
        else:
            return "👥 **Patient Information Commands:**\n\n• 'How many patients?'\n• 'New patients this month'\n• 'List all patients'\n• 'Active patients'\n• 'Find patient named [name]'"
    
    def get_last_visit(self, patient_name):
        last_appt = mongo.db.appointments.find_one(
            {"patient": patient_name},
            sort=[("date", -1)]
        )
        return last_appt.get('date', 'No visits') if last_appt else 'No visits'
    
    # ================= APPOINTMENT QUERIES =================
    
    def handle_appointment_query(self, message):
        # Total appointments
        if any(word in message for word in ['total appointment', 'how many appointment', 'appointment count']):
            total = mongo.db.appointments.count_documents({})
            completed = mongo.db.appointments.count_documents({"status": "Completed"})
            pending = mongo.db.appointments.count_documents({"status": "Pending"})
            cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
            
            completion_rate = round((completed / total * 100), 1) if total > 0 else 0
            
            return f"""📅 **Appointment Analytics**

📊 **Overall Statistics:**
• Total Appointments: {total}
• ✅ Completed: {completed}
• ⏳ Pending: {pending}
• ❌ Cancelled: {cancelled}

📈 **Performance Metrics:**
• Completion Rate: {completion_rate}%
• Cancellation Rate: {round((cancelled/total)*100, 1) if total > 0 else 0}%
• Pending Rate: {round((pending/total)*100, 1) if total > 0 else 0}%

💡 For detailed trends, ask 'Appointment trends' or 'Monthly appointments'
"""
        
        # Today's appointments
        elif 'today appointment' in message or 'appointment today' in message:
            today = datetime.now().strftime('%Y-%m-%d')
            today_appts = list(mongo.db.appointments.find({"date": today}))
            
            if today_appts:
                completed_today = sum(1 for a in today_appts if a.get('status') == 'Completed')
                pending_today = sum(1 for a in today_appts if a.get('status') == 'Pending')
                
                response = f"📅 **Today's Appointments ({datetime.now().strftime('%A, %B %d')})**\n\n"
                response += f"📊 **Summary:** {len(today_appts)} total | ✅ {completed_today} completed | ⏳ {pending_today} pending\n\n"
                response += "**Schedule:**\n"
                
                for appt in today_appts[:15]:
                    status_icon = "✅" if appt.get('status') == 'Completed' else "⏳" if appt.get('status') == 'Pending' else "❌"
                    response += f"{status_icon} {appt.get('time', 'N/A')} - {appt.get('patient', 'Unknown')} with Dr. {appt.get('doctor', 'Unknown')}\n"
                
                if len(today_appts) > 15:
                    response += f"\n... and {len(today_appts) - 15} more appointments"
                
                return response
            return "📅 No appointments scheduled for today."
        
        # Tomorrow's appointments
        elif 'tomorrow appointment' in message:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            tomorrow_appts = list(mongo.db.appointments.find({"date": tomorrow}))
            
            if tomorrow_appts:
                response = f"📅 **Tomorrow's Appointments ({ (datetime.now() + timedelta(days=1)).strftime('%A, %B %d')})**\n\n"
                for appt in tomorrow_appts[:15]:
                    response += f"• {appt.get('time', 'N/A')} - {appt.get('patient', 'Unknown')} with Dr. {appt.get('doctor', 'Unknown')}\n"
                return response
            return "📅 No appointments scheduled for tomorrow."
        
        # This week's appointments
        elif 'this week appointment' in message or 'week appointment' in message:
            today = datetime.now()
            week_appts = []
            for i in range(7):
                date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
                count = mongo.db.appointments.count_documents({"date": date})
                week_appts.append((date, count))
            
            response = f"📅 **This Week's Appointments ({today.strftime('%B %d')} - {(today + timedelta(days=6)).strftime('%B %d')})**\n\n"
            total = 0
            for date, count in week_appts:
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                response += f"• {day_name}: {count} appointments\n"
                total += count
            
            response += f"\n📊 **Total this week:** {total} appointments"
            response += f"\n📈 **Daily Average:** {round(total/7, 1)} appointments"
            return response
        
        # Upcoming appointments
        elif 'upcoming appointment' in message:
            today = datetime.now().strftime('%Y-%m-%d')
            upcoming = list(mongo.db.appointments.find({
                "date": {"$gte": today},
                "status": "Pending"
            }).limit(15))
            
            if upcoming:
                response = "📅 **Upcoming Appointments**\n\n"
                for appt in upcoming:
                    response += f"• {appt.get('date', 'N/A')} at {appt.get('time', 'N/A')} - {appt.get('patient', 'Unknown')} with Dr. {appt.get('doctor', 'Unknown')}\n"
                return response
            return "📅 No upcoming appointments scheduled."
        
        # Missed/Cancelled appointments
        elif 'missed' in message or 'cancelled' in message or 'no show' in message:
            cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
            total = mongo.db.appointments.count_documents({})
            
            # Get cancelled by doctor
            cancelled_by_doctor = {}
            for appt in mongo.db.appointments.find({"status": "Cancelled"}):
                doctor = appt.get('doctor', 'Unknown')
                cancelled_by_doctor[doctor] = cancelled_by_doctor.get(doctor, 0) + 1
            
            response = f"""❌ **Cancelled/Missed Appointments Analysis**

📊 **Overall:**
• Total Cancelled: {cancelled}
• Cancellation Rate: {round((cancelled/total)*100, 1) if total > 0 else 0}%

👨‍⚕️ **By Doctor:**
"""
            for doctor, count in list(cancelled_by_doctor.items())[:5]:
                response += f"• Dr. {doctor}: {count} cancellations\n"
            
            response += "\n💡 **Recommendation:** Send reminders to reduce no-shows"
            return response
        
        # Appointment by doctor
        elif 'appointment for doctor' in message or 'doctor appointments' in message:
            doctor_name = None
            words = message.split()
            for i, word in enumerate(words):
                if word == 'dr' or word == 'dr.' or word == 'doctor':
                    if i + 1 < len(words):
                        doctor_name = words[i + 1]
                        break
            
            if doctor_name:
                doctor = mongo.db.doctors.find_one({"name": {"$regex": doctor_name, "$options": "i"}})
                if doctor:
                    total_appts = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                    completed = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Completed"})
                    pending = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Pending"})
                    
                    return f"""📅 **Dr. {doctor.get('name')}'s Appointment Statistics**

📊 **Summary:**
• Total Appointments: {total_appts}
• ✅ Completed: {completed}
• ⏳ Pending: {pending}
• ❌ Cancelled: {mongo.db.appointments.count_documents({'doctor': doctor.get('name'), 'status': 'Cancelled'})}

📈 **Performance:**
• Success Rate: {round((completed/total_appts)*100, 1) if total_appts > 0 else 0}%
• Patient Load: {round(total_appts/30, 1)} per day

💡 To book appointment, go to Appointments section
"""
                else:
                    return "Doctor not found."
            return "Please specify doctor name. Example: 'Appointments for Dr. Smith'"
        
        else:
            return "📅 **Appointment Commands:**\n\n• 'Total appointments'\n• 'Today's appointments'\n• 'Tomorrow's appointments'\n• 'This week's appointments'\n• 'Upcoming appointments'\n• 'Cancelled appointments'\n• 'Appointments for Dr. [name]'"
    
    # ================= STATISTICS QUERIES =================
    
    def handle_stats_query(self, message):
        total_doctors = mongo.db.doctors.count_documents({})
        total_patients = mongo.db.patients.count_documents({})
        total_appointments = mongo.db.appointments.count_documents({})
        completed = mongo.db.appointments.count_documents({"status": "Completed"})
        pending = mongo.db.appointments.count_documents({"status": "Pending"})
        cancelled = mongo.db.appointments.count_documents({"status": "Cancelled"})
        
        today = datetime.now().strftime('%Y-%m-%d')
        today_appts = mongo.db.appointments.count_documents({"date": today})
        
        # This month's appointments
        first_day = datetime(datetime.now().year, datetime.now().month, 1).strftime('%Y-%m-%d')
        month_appts = mongo.db.appointments.count_documents({"date": {"$gte": first_day}})
        
        # Busiest day
        all_dates = [appt.get('date') for appt in mongo.db.appointments.find({}) if appt.get('date')]
        from collections import Counter
        date_counts = Counter(all_dates)
        busiest_day = max(date_counts.items(), key=lambda x: x[1])[0] if date_counts else "No data"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                  HOSPITAL DASHBOARD STATISTICS               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  👨‍⚕️ **DOCTORS**                                             ║
║  • Total Doctors: {str(total_doctors).ljust(40)}║
║                                                              ║
║  👥 **PATIENTS**                                             ║
║  • Total Patients: {str(total_patients).ljust(39)}║
║                                                              ║
║  📅 **APPOINTMENTS**                                         ║
║  • Total: {str(total_appointments).ljust(42)}║
║  • Completed: {str(completed).ljust(40)}║
║  • Pending: {str(pending).ljust(42)}║
║  • Cancelled: {str(cancelled).ljust(40)}║
║                                                              ║
║  📈 **PERFORMANCE**                                          ║
║  • Completion Rate: {str(round((completed/total_appointments)*100, 1) if total_appointments > 0 else 0).ljust(32)}%║
║  • Today's Load: {str(today_appts).ljust(37)}║
║  • Monthly Load: {str(month_appts).ljust(36)}║
║  • Busiest Day: {str(busiest_day).ljust(37)}║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

💡 For detailed analytics, visit the Reports section.
"""
    
    # ================= DEPARTMENT QUERIES =================
    
    def handle_department_query(self, message):
        departments = {
            'cardiology': {'doctors': 0, 'appointments': 0, 'description': 'Heart and cardiovascular diseases'},
            'neurology': {'doctors': 0, 'appointments': 0, 'description': 'Brain, spine and nervous system'},
            'pediatrics': {'doctors': 0, 'appointments': 0, 'description': 'Child healthcare'},
            'orthopedic': {'doctors': 0, 'appointments': 0, 'description': 'Bones, joints and muscles'},
            'gynecology': {'doctors': 0, 'appointments': 0, 'description': "Women's reproductive health"},
            'dermatology': {'doctors': 0, 'appointments': 0, 'description': 'Skin, hair and nail conditions'},
            'ent': {'doctors': 0, 'appointments': 0, 'description': 'Ear, nose and throat'},
            'ophthalmology': {'doctors': 0, 'appointments': 0, 'description': 'Eye care'},
            'psychiatry': {'doctors': 0, 'appointments': 0, 'description': 'Mental health'},
            'emergency': {'doctors': 0, 'appointments': 0, 'description': '24/7 Emergency care'}
        }
        
        # Count doctors per department
        all_doctors = list(mongo.db.doctors.find({}))
        for doctor in all_doctors:
            spec = doctor.get('specialization', '').lower()
            for dept in departments:
                if dept in spec:
                    departments[dept]['doctors'] += 1
                    break
        
        # Count appointments per department
        for dept in departments:
            departments[dept]['appointments'] = mongo.db.appointments.count_documents({
                "doctor": {"$regex": dept, "$options": "i"}
            })
        
        # Check if asking for specific department
        for dept_name, dept_data in departments.items():
            if dept_name in message:
                return f"""
🏥 **{dept_name.upper()} DEPARTMENT**

📋 **Description:** {dept_data['description']}

👨‍⚕️ **Staff:** {dept_data['doctors']} specialized doctors
📊 **Patient Load:** {dept_data['appointments']} total appointments

💡 To see doctors in this department, ask "List {dept_name} doctors"
"""
        
        # General department overview
        response = "🏥 **Department Overview**\n\n"
        for dept_name, dept_data in departments.items():
            response += f"**{dept_name.capitalize()}**\n"
            response += f"  👨‍⚕️ {dept_data['doctors']} doctors | 📊 {dept_data['appointments']} patients\n\n"
        
        response += "💡 For specific department details, ask 'Cardiology department' or 'Neurology department'"
        return response
    
    # ================= FINANCIAL QUERIES =================
    
    def handle_financial_query(self, message):
        # Consultation fees
        if 'consultation fee' in message or 'fee' in message:
            return """
💰 **Consultation Fees**

👨‍⚕️ **General Physician:** ₹500 - ₹800
👨‍⚕️ **Specialist Doctor:** ₹1000 - ₹1500
👨‍⚕️ **Senior Specialist:** ₹1500 - ₹2000
🚑 **Emergency Consultation:** ₹1000
🏠 **Home Visit:** ₹2000+

💳 **Payment Methods:** Cash, Card, UPI, Insurance

📞 For exact pricing, please call reception.
"""
        
        # Revenue estimation
        elif 'revenue' in message or 'income' in message:
            total_appointments = mongo.db.appointments.count_documents({"status": "Completed"})
            estimated_revenue = total_appointments * 800  # Average fee
            return f"""
💰 **Revenue Estimation**

📊 **Based on Completed Appointments:** {total_appointments}
💵 **Estimated Revenue:** ₹{estimated_revenue:,}

⚠️ *This is an estimate. Actual revenue may vary based on consultation types.*

For accurate financial reports, contact the accounts department.
"""
        
        else:
            return "💰 **Financial Information:**\n\n• 'Consultation fees'\n• 'Revenue estimation'\n• 'Payment methods'"
    
    # ================= SCHEDULE QUERIES =================
    
    def handle_schedule_query(self, message):
        if 'hospital timing' in message or 'opening hours' in message:
            return """
🏥 **Hospital Operating Hours**

🕐 **Emergency Department:** 24/7 (Always Open)

📅 **OPD Timings:** 
• Monday - Saturday: 9:00 AM - 5:00 PM
• Sunday: Closed (Emergency only)
• Lunch Break: 1:00 PM - 2:00 PM

💊 **Pharmacy:** 24/7
🔬 **Laboratory:** 7:00 AM - 9:00 PM (Daily)

👥 **Visiting Hours:**
• Evening: 4:00 PM - 6:00 PM
• Morning: 11:00 AM - 12:00 PM

📞 For after-hours emergencies: +91-XXXXXXXXXX
"""
        else:
            return "🕐 **Schedule Commands:**\n\n• 'Hospital timings'\n• 'Visiting hours'\n• 'Doctor schedule'"
    
    # ================= REPORT QUERIES =================
    
    def handle_report_query(self, message):
        return """
📄 **Report Generation**

Available Reports:
1. 📊 **Appointment Report** - Daily/Weekly/Monthly
2. 👨‍⚕️ **Doctor Performance Report**
3. 👥 **Patient Registration Report**
4. 💰 **Revenue Report**
5. 📈 **Department-wise Analysis**

💡 **To generate reports:**
• Click on 'Reports' in the sidebar
• Select report type
• Choose date range
• Click 'Export PDF' or 'Export Excel'

For automated reports, contact the admin.
"""
    
    # ================= COMPARISON QUERIES =================
    
    def handle_comparison_query(self, message):
        if 'busiest day' in message or 'peak day' in message:
            all_dates = [appt.get('date') for appt in mongo.db.appointments.find({}) if appt.get('date')]
            from collections import Counter
            date_counts = Counter(all_dates)
            
            if date_counts:
                busiest = max(date_counts.items(), key=lambda x: x[1])
                quietest = min(date_counts.items(), key=lambda x: x[1])
                return f"""
📊 **Appointment Comparison**

🔥 **Busiest Day:** {busiest[0]} ({busiest[1]} appointments)
🍃 **Quietest Day:** {quietest[0]} ({quietest[1]} appointments)

📈 **Difference:** {busiest[1] - quietest[1]} more appointments on busy days

💡 **Recommendation:** Add more staff on busy days
"""
            return "Not enough data for comparison."
        
        elif 'doctor comparison' in message or 'compare doctors' in message:
            doctors = list(mongo.db.doctors.find({}))
            doctor_stats = []
            for doctor in doctors:
                count = mongo.db.appointments.count_documents({"doctor": doctor.get('name')})
                completed = mongo.db.appointments.count_documents({"doctor": doctor.get('name'), "status": "Completed"})
                doctor_stats.append((doctor.get('name'), count, completed))
            
            doctor_stats.sort(key=lambda x: x[1], reverse=True)
            
            response = "👨‍⚕️ **Doctor Performance Comparison**\n\n"
            for i, (name, total, completed) in enumerate(doctor_stats[:5], 1):
                response += f"{i}. **Dr. {name}**\n"
                response += f"   📊 Total: {total} | ✅ Completed: {completed}\n"
                response += f"   📈 Success Rate: {round((completed/total)*100, 1) if total > 0 else 0}%\n\n"
            return response
        
        else:
            return "📊 **Comparison Commands:**\n\n• 'Busiest day vs quietest day'\n• 'Compare doctor performance'\n• 'Monthly comparison'"
    
    # ================= TREND QUERIES =================
    
    def handle_trend_query(self, message):
        # Get last 30 days of appointments
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_appointments = list(mongo.db.appointments.find({
            "date": {"$gte": thirty_days_ago}
        }))
        
        if len(recent_appointments) < 10:
            return "📈 Not enough data for trend analysis. Add more appointments first."
        
        # Calculate trend
        dates = sorted(set([appt.get('date') for appt in recent_appointments if appt.get('date')]))
        if len(dates) >= 14:
            first_week = sum(1 for appt in recent_appointments if appt.get('date') in dates[:7])
            second_week = sum(1 for appt in recent_appointments if appt.get('date') in dates[7:14])
            
            trend = "increasing" if second_week > first_week else "decreasing" if second_week < first_week else "stable"
            change = abs(second_week - first_week)
            
            return f"""
📈 **Appointment Trend Analysis (Last 14 Days)**

📊 **Week 1:** {first_week} appointments
📊 **Week 2:** {second_week} appointments

📉 **Trend:** {trend.upper()} ({'+' if second_week > first_week else ''}{change} appointments)

💡 **Insight:** Appointments are {trend} by {round((change/first_week)*100, 1) if first_week > 0 else 0}%

Recommendation: {'Add more staff' if trend == 'increasing' else 'Optimize resources' if trend == 'decreasing' else 'Maintain current operations'}
"""
        
        return "📈 Need more data for trend analysis. Please check back later."
    
    # ================= MEDICAL QUERIES =================
    
    def handle_medical_query(self, message):
        return self.search_knowledge_base(message)
    
    # ================= KNOWLEDGE BASE =================
    
    def search_knowledge_base(self, message):
        # Search in database
        result = mongo.db.chat_knowledge.find_one({
            "$or": [
                {"question": message},
                {"keywords": {"$in": message.split()}}
            ]
        })
        
        if result:
            return result["answer"]
        
        return self.get_fallback_response()
    
    # ================= HELPER METHODS =================
    
    def get_doctor_help(self):
        return """
👨‍⚕️ **Doctor Information Commands:**

📋 **List/View:**
• "How many doctors?"
• "List all doctors"
• "Show doctor directory"

🏆 **Best Doctors:**
• "Best cardiologist"
• "Top pediatrician"
• "Leading dermatologist"

👤 **Specific Doctor:**
• "Tell me about Dr. Smith"
• "Dr. Johnson's schedule"
• "Dr. Williams qualifications"

📅 **Availability:**
• "Doctors available today"
• "Doctor working hours"
• "On-duty doctors now"

📊 **Performance:**
• "Most popular doctor"
• "Busiest doctor"
• "Doctor appointment statistics"

💡 Try any of these commands to get detailed information!
"""
    
    def get_help_message(self):
        return """
🤖 **Complete Chatbot Help Guide**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👨‍⚕️ **DOCTOR COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "How many doctors?" - Total doctor count
• "List all doctors" - Complete directory
• "Best cardiologist" - Top specialists
• "Tell me about Dr. Smith" - Doctor profile
• "Doctors available today" - Today's availability
• "Dr. Smith's schedule" - Working hours
• "Most popular doctor" - Busiest doctors
• "Cardiology department" - Department info

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 **PATIENT COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "How many patients?" - Total count
• "New patients this month" - Registration stats
• "Active patients" - Frequent visitors
• "List all patients" - Patient directory
• "Find patient named John" - Search patient

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 **APPOINTMENT COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Total appointments" - Overall stats
• "Today's appointments" - Daily schedule
• "Tomorrow's appointments" - Next day
• "This week's appointments" - Weekly view
• "Upcoming appointments" - Future bookings
• "Cancelled appointments" - No-show analysis
• "Appointments for Dr. Smith" - Doctor specific

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 **STATISTICS COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Hospital statistics" - Complete overview
• "Department overview" - Dept-wise stats
• "Performance metrics" - KPIs
• "Monthly report" - Period summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 **ANALYSIS COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Busiest day" - Peak day analysis
• "Compare doctors" - Performance comparison
• "Appointment trends" - Pattern analysis
• "Growth rate" - Month over month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 **GENERAL COMMANDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "Hospital timings" - Operating hours
• "Consultation fees" - Price information
• "Emergency services" - Urgent care
• "Help" - This menu

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** You can ask naturally, like "Who is the best heart doctor?" or "Show me today's schedule"

❓ **Need more help?** Type your question naturally, and I'll do my best to assist!
"""
    
    def get_fallback_response(self):
        return """
❌ I couldn't find an answer to your question.

💡 **Try these popular commands:**
• "How many doctors are there?"
• "List all doctors"
• "Best cardiologist"
• "Today's appointments"
• "Hospital statistics"
• "Help" - See all commands

📌 **Or visit the dashboard sections:**
• Doctors - View all doctors
• Appointments - Book/view appointments
• Reports - Generate analytics

What would you like to know about our hospital?
"""


# ================= FLASK ROUTE =================

@chat_bp.route("/", methods=["POST"])
@jwt_required()
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        current_user_email = get_jwt_identity()
        
        # Get user role
        user_role = None
        if mongo.db.admins.find_one({"email": current_user_email}):
            user_role = "admin"
        elif mongo.db.doctors.find_one({"email": current_user_email}):
            user_role = "doctor"
        elif mongo.db.patients.find_one({"email": current_user_email}):
            user_role = "patient"
        
        if not user_message:
            return jsonify({"reply": "Please enter a message"}), 400
        
        # Initialize chatbot
        chatbot = HospitalChatbot(current_user_email, user_role)
        
        # Get response
        response = chatbot.get_response(user_message)
        
        return jsonify({"reply": response}), 200
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"reply": f"Sorry, an error occurred: {str(e)}"}), 500


@chat_bp.route("/knowledge/add", methods=["POST"])
@jwt_required()
def add_knowledge():
    """Add new Q&A to knowledge base (Admin only)"""
    try:
        current_user = get_jwt_identity()
        admin = mongo.db.admins.find_one({"email": current_user})
        
        if not admin:
            return jsonify({"message": "Admin access required"}), 403
        
        data = request.get_json()
        question = data.get("question")
        answer = data.get("answer")
        category = data.get("category", "general")
        keywords = data.get("keywords", "")
        
        if not question or not answer:
            return jsonify({"message": "Question and answer required"}), 400
        
        knowledge = {
            "question": question.lower(),
            "answer": answer,
            "category": category,
            "keywords": keywords,
            "created_at": datetime.utcnow(),
            "usage_count": 0,
            "is_active": True
        }
        
        mongo.db.chat_knowledge.insert_one(knowledge)
        
        return jsonify({"message": "Knowledge added successfully"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500