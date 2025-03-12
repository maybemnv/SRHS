from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'doctor'
    records = db.relationship('HealthRecord', backref='owner', lazy='dynamic')
    # Add relationship for doctor access
    doctor_access = db.relationship('DoctorAccess', 
                                  foreign_keys='DoctorAccess.patient_id',
                                  backref='patient', 
                                  lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def grant_access_to_doctor(self, doctor_id):
        if not DoctorAccess.query.filter_by(
            patient_id=self.id, 
            doctor_id=doctor_id
        ).first():
            access = DoctorAccess(patient_id=self.id, doctor_id=doctor_id)
            db.session.add(access)
            db.session.commit()

    def revoke_access_from_doctor(self, doctor_id):
        access = DoctorAccess.query.filter_by(
            patient_id=self.id, 
            doctor_id=doctor_id
        ).first()
        if access:
            db.session.delete(access)
            db.session.commit()

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    record_type = db.Column(db.String(50))
    file_path = db.Column(db.String(255))  # Path to uploaded file
    file_type = db.Column(db.String(50))   # Type of the uploaded file
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DoctorAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_date = db.Column(db.DateTime, default=datetime.utcnow)
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='patient_accesses')
