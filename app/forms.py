from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from app.models import User


class CollectionForm(FlaskForm):
    level = IntegerField('Level', validators=[DataRequired(), NumberRange(min=0, max=7)])
    awaken = IntegerField('Awaken', validators=[DataRequired(), NumberRange(min=0, max=7)])
    wpn = IntegerField('Weapon Level', validators=[DataRequired(), NumberRange(min=0, max=9)])
    medals = IntegerField('Medals', validators=[DataRequired(), NumberRange(min=0, max=2500)])
    submit = SubmitField('Save Changes')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter a username")])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter a password")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Please enter a username")])
    email = StringField('Email', validators=[DataRequired(message="Please enter a valid email"), Email()])
    password = PasswordField('Password', validators=[DataRequired(message="Please enter a password")])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(message="Passwords doesn't match"), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is not available')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email is not available')