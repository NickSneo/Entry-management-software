from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import TelField


class RegistrationForm(FlaskForm):
    name = StringField('Guest name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Guest Email', validators=[DataRequired(), Email()])
    tel = TelField('Guest Tel', widget = widgets.Input(input_type="tel"), validators=[DataRequired()])
    passkey = PasswordField('Passkey', validators=[DataRequired()])
    checkin_time = DateTimeField('Checkin Time', validators=[DataRequired()], default=datetime.now(), format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('')


# class LoginForm(FlaskForm):
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember = BooleanField('Remember Me')
#     submit = SubmitField('Login')