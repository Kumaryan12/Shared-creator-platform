from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Optional, URL, Email, Length
from app import db



class RequirementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('hackathon', 'Hackathon'),
        ('books', 'Books'),
        ('collaboration', 'Collaboration'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    contact_info = StringField('Contact Information', validators=[DataRequired()])
    submit = SubmitField('Post Requirement')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    bio = TextAreaField('Bio', validators=[Optional()])
    skills = StringField('Skills', validators=[Optional()])
    submit = SubmitField('Register')
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[Optional()])
    skills = StringField('Skills (comma-separated)', validators=[Optional()])
    submit = SubmitField('Save Changes')



