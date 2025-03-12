from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')])
    submit = SubmitField('Register')

class HealthRecordForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    record_type = SelectField('Record Type', choices=[
        ('general', 'General'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('diagnosis', 'Diagnosis')
    ])
    content = TextAreaField('Description', validators=[DataRequired()])
    file = FileField('Upload Report', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'jpg', 'png'], 'Please upload PDF or image files only!')
    ])
    submit = SubmitField('Save Record')

class DoctorAccessForm(FlaskForm):
    doctor_email = StringField('Doctor\'s Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Grant Access')
