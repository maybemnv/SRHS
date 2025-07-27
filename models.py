# Only import db (and login_manager if needed) from app.py to avoid circular imports
from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_reports = db.relationship('MedicalReport', backref='patient', lazy=True, cascade='all, delete-orphan')
    granted_accesses = db.relationship('DoctorAccess', foreign_keys='DoctorAccess.patient_id', backref='patient', lazy=True, cascade='all, delete-orphan')
    doctor_accesses = db.relationship('DoctorAccess', foreign_keys='DoctorAccess.doctor_id', backref='doctor', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

class MedicalReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MedicalReport {self.disease_name}>'

class DoctorAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a patient can't grant access to the same doctor twice
    __table_args__ = (db.UniqueConstraint('patient_id', 'doctor_id', name='unique_patient_doctor_access'),)
    
    def __repr__(self):
        return f'<DoctorAccess Patient:{self.patient_id} Doctor:{self.doctor_id}>'
