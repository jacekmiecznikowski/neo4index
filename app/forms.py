from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class SignupForm(FlaskForm):
	first_name = StringField('First name', validators=[DataRequired("Please enter your first name.")])
	last_name = StringField('Last name', validators=[DataRequired("Please enter your last name.")])
	username = StringField('Username', validators=[DataRequired("Please enter your username."), Length(min=3, max=15, message="Username must be at least 3 and no more than 15 characters long")])
	password = PasswordField('Password', validators=[DataRequired("Please enter your password."), Length(min=8, message="Password must be at least 8 characters long")])
	submit = SubmitField('Register new account')


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired("Please enter your username.")])
	password = PasswordField('Password', validators=[DataRequired("Please enter your password.")])
	submit = SubmitField('Sign in')