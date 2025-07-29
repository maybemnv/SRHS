import os
import secrets
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app import app, db
from models import User, MedicalReport, DoctorAccess
from chatbot import process_chatbot_query

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name'].strip()
        
        # Validation
        if not all([username, email, password, role, full_name]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if role not in ['patient', 'doctor']:
            flash('Invalid role selected.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            full_name=full_name
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            current_app.logger.error(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome, {user.full_name}!', 'success')
            
            # Redirect based on role
            if user.role == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('index'))
    
    # Get patient's reports
    reports = MedicalReport.query.filter_by(patient_id=current_user.id).order_by(MedicalReport.upload_date.desc()).all()
    
    # Get granted accesses
    granted_accesses = db.session.query(DoctorAccess, User).join(
        User, DoctorAccess.doctor_id == User.id
    ).filter(DoctorAccess.patient_id == current_user.id).all()
    
    return render_template('patient_dashboard.html', reports=reports, granted_accesses=granted_accesses)

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('index'))
    
    # Get patients who granted access to this doctor
    patient_accesses = db.session.query(DoctorAccess, User).join(
        User, DoctorAccess.patient_id == User.id
    ).filter(DoctorAccess.doctor_id == current_user.id).all()
    
    # Get reports for each patient
    patients_data = []
    for access, patient in patient_accesses:
        reports = MedicalReport.query.filter_by(patient_id=patient.id).order_by(MedicalReport.upload_date.desc()).all()
        patients_data.append({
            'patient': patient,
            'reports': reports,
            'access_date': access.granted_date
        })
    
    # Analytics data
    total_patients = len(patients_data)
    
    # Disease statistics
    disease_stats = {}
    for patient_data in patients_data:
        for report in patient_data['reports']:
            disease = report.disease_name
            disease_stats[disease] = disease_stats.get(disease, 0) + 1
    
    return render_template('doctor_dashboard.html', 
                         patients_data=patients_data, 
                         total_patients=total_patients,
                         disease_stats=disease_stats)

@app.route('/upload_report', methods=['GET', 'POST'])
@login_required
def upload_report():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        disease_name = request.form['disease_name'].strip()
        description = request.form['description'].strip()
        
        if not disease_name or not description:
            flash('Disease name and description are required.', 'error')
            return render_template('upload_report.html')
        
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload_report.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload_report.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{secrets.token_hex(8)}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(file_path)
                report = MedicalReport(
                    patient_id=current_user.id,
                    disease_name=disease_name,
                    description=description,
                    file_path=file_path,
                    file_name=filename,
                    file_type=filename.rsplit('.', 1)[1].lower()
                )
                db.session.add(report)
                db.session.commit()
                flash('Medical report uploaded successfully!', 'success')
                return redirect(url_for('patient_dashboard'))
            except Exception as e:
                db.session.rollback()
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash('Failed to upload report. Please try again.', 'error')
                current_app.logger.error(f"Upload error: {e}")
        else:
            flash('Invalid file type. Please upload PDF, DOC, DOCX, or image files.', 'error')
    
    return render_template('upload_report.html')

@app.route('/grant_access', methods=['GET', 'POST'])
@login_required
def grant_access():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        doctor_email = request.form['doctor_email'].strip()
        
        if not doctor_email:
            flash('Doctor email is required.', 'error')
            return render_template('grant_access.html')
        
        # Find doctor by email
        doctor = User.query.filter_by(email=doctor_email, role='doctor').first()
        
        if not doctor:
            flash('No doctor found with this email address.', 'error')
            return render_template('grant_access.html')
        
        # Check if access already granted
        existing_access = DoctorAccess.query.filter_by(
            patient_id=current_user.id,
            doctor_id=doctor.id
        ).first()
        
        if existing_access:
            flash(f'Access already granted to Dr. {doctor.full_name}.', 'warning')
            return render_template('grant_access.html')
        
        # Grant access
        try:
            access = DoctorAccess(
                patient_id=current_user.id,
                doctor_id=doctor.id
            )
            db.session.add(access)
            db.session.commit()
            
            flash(f'Access granted to Dr. {doctor.full_name} successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to grant access. Please try again.', 'error')
            current_app.logger.error(f"Grant access error: {e}")
    
    return render_template('grant_access.html')

@app.route('/download/<int:report_id>')
@login_required
def download_file(report_id):
    report = MedicalReport.query.get_or_404(report_id)
    
    # Check access permissions
    if current_user.role == 'patient':
        if report.patient_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('patient_dashboard'))
    elif current_user.role == 'doctor':
        access = DoctorAccess.query.filter_by(
            patient_id=report.patient_id,
            doctor_id=current_user.id
        ).first()
        if not access:
            flash('Access denied.', 'error')
            return redirect(url_for('doctor_dashboard'))
    else:
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    try:
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            os.path.basename(report.file_path),
            as_attachment=True,
            download_name=report.file_name
        )
    except FileNotFoundError:
        flash('File not found.', 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/chatbot', methods=['POST'])
@login_required
def chatbot():
    query = request.json.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        data_for_chatbot = []
        if current_user.role == 'doctor':
            # For doctors, get all accessible patients' data
            patient_accesses = db.session.query(DoctorAccess, User).join(
                User, DoctorAccess.patient_id == User.id
            ).filter(DoctorAccess.doctor_id == current_user.id).all()
            
            for access, patient in patient_accesses:
                reports = MedicalReport.query.filter_by(patient_id=patient.id).all()
                data_for_chatbot.append({
                    'patient': patient,
                    'reports': reports
                })
        
        elif current_user.role == 'patient':
            # For patients, get their own data
            reports = MedicalReport.query.filter_by(patient_id=current_user.id).all()
            data_for_chatbot.append({
                'patient': current_user,
                'reports': reports
            })

        response = process_chatbot_query(query, data_for_chatbot, current_user.role)
        return jsonify({'response': response})
        
    except Exception as e:
        current_app.logger.error(f"Chatbot error: {e}")
        return jsonify({'error': 'Failed to process query'}), 500

@app.route('/revoke_access/<int:access_id>', methods=['POST'])
@login_required
def revoke_access(access_id):
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Find the access record
        access = DoctorAccess.query.filter_by(
            id=access_id,
            patient_id=current_user.id
        ).first()
        
        if not access:
            flash('Access record not found.', 'error')
            return redirect(url_for('patient_dashboard'))
        
        # Get doctor info for flash message
        doctor = User.query.get(access.doctor_id)
        doctor_name = doctor.full_name if doctor else "Unknown Doctor"
        
        # Delete the access record
        db.session.delete(access)
        db.session.commit()
        
        flash(f'Access revoked for Dr. {doctor_name} successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to revoke access. Please try again.', 'error')
        current_app.logger.error(f"Revoke access error: {e}")
    
    return redirect(url_for('patient_dashboard'))

@app.route('/api/analytics')
@login_required
def analytics_api():
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get patients who granted access to this doctor
        patient_accesses = db.session.query(DoctorAccess, User).join(
            User, DoctorAccess.patient_id == User.id
        ).filter(DoctorAccess.doctor_id == current_user.id).all()
        
        # Disease statistics
        disease_stats = {}
        total_patients = len(patient_accesses)
        
        for access, patient in patient_accesses:
            reports = MedicalReport.query.filter_by(patient_id=patient.id).all()
            for report in reports:
                disease = report.disease_name
                disease_stats[disease] = disease_stats.get(disease, 0) + 1
        
        return jsonify({
            'total_patients': total_patients,
            'disease_stats': disease_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Analytics error: {e}")
        return jsonify({'error': 'Failed to get analytics data'}), 500



    try:
        # Get patient's reports
        reports = MedicalReport.query.filter_by(patient_id=current_user.id).all()
        # Get granted doctor accesses
        granted_accesses = db.session.query(DoctorAccess, User).join(
            User, DoctorAccess.doctor_id == User.id
        ).filter(DoctorAccess.patient_id == current_user.id).all()
        # Prepare data for chatbot logic
        patient_data = {
            'patient': current_user,
            'reports': reports,
            'granted_accesses': granted_accesses
        }
        from chatbot import process_patient_chatbot_query
        response = process_patient_chatbot_query(query, patient_data)
        return jsonify({'response': response})
    except Exception as e:
        current_app.logger.error(f"Patient Chatbot error: {e}")
        return jsonify({'error': 'Failed to process query'}), 500
