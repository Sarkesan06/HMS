from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # admin, doctor, patient


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    specialization = db.Column(db.String(100))
    available_slots = db.Column(db.String(200))


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    age = db.Column(db.Integer)
    allergies = db.Column(db.String(200))
    medications = db.Column(db.String(200))


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    date = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class ChatKnowledge(db.Model):
    """Stores Q&A pairs for the chatbot"""
    __tablename__ = 'chat_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False, unique=True)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='general')
    keywords = db.Column(db.String(500))  # Comma-separated keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)  # Track how often this is used
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ChatKnowledge {self.question[:50]}>'

class ChatConversation(db.Model):
    """Stores user conversations for learning"""
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    was_helpful = db.Column(db.Boolean, default=None)  # User feedback
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatConversation {self.id}>'