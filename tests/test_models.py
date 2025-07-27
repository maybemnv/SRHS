import unittest
from app import app, db
from models import User, MedicalReport, DoctorAccess
from datetime import datetime

class TestModelUnit(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        user = User(
            username="test_user",
            email="test@example.com",
            password_hash="hashedpass",
            role="patient",
            full_name="Test User"
        )
        db.session.add(user)
        db.session.commit()
        fetched = User.query.filter_by(username="test_user").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.email, "test@example.com")

    def test_create_medical_report(self):
        user = User(
            username="report_user",
            email="report@example.com",
            password_hash="hash",
            role="patient",
            full_name="Report User"
        )
        db.session.add(user)
        db.session.commit()

        report = MedicalReport(
            patient_id=user.id,
            disease_name="Flu",
            description="Mild symptoms",
            file_path="uploads/flu.pdf",
            file_name="flu.pdf",
            file_type="pdf"
        )
        db.session.add(report)
        db.session.commit()

        fetched = MedicalReport.query.filter_by(patient_id=user.id).first()
        self.assertEqual(fetched.disease_name, "Flu")
        self.assertEqual(fetched.file_type, "pdf")

    def test_doctor_access_uniqueness(self):
        patient = User(
            username="patient1",
            email="p1@example.com",
            password_hash="hash1",
            role="patient",
            full_name="Patient One"
        )
        doctor = User(
            username="doctor1",
            email="d1@example.com",
            password_hash="hash2",
            role="doctor",
            full_name="Doctor One"
        )
        db.session.add_all([patient, doctor])
        db.session.commit()

        access1 = DoctorAccess(patient_id=patient.id, doctor_id=doctor.id)
        db.session.add(access1)
        db.session.commit()

        access2 = DoctorAccess(patient_id=patient.id, doctor_id=doctor.id)
        db.session.add(access2)
        
        with self.assertRaises(Exception):
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

if __name__ == '__main__':
    unittest.main()
