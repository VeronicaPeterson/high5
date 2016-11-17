from flask_wtf import Form
from wtforms import StringField, PasswordField
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms.validators import DataRequired, InputRequired, ValidationError, Email
from models import User

'''
Login form. Requires user to enter user_name and password. Validates that the user exists in the
database and that the password is correct.
'''
class LoginForm(Form):
    user_name = StringField('user_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

    def validate_password(form, field):
        try:
            user = User.query.filter(User.user_name == form.user_name.data).one()
        except (MultipleResultsFound, NoResultFound):
            raise ValidationError("Invalid user")
        if user is None:
            raise ValidationError("Invalid user")
        if not user.is_valid_password(form.password.data):
            raise ValidationError("Invalid password")
        form.user = user
        return user

'''
Registration form to register a new User to the site. Allows a new register to pick a unique
username and requires them to enter a name, email, and select a password. Validates that no
user currently exists with the given username.'''
class RegistrationForm(Form):
    user_name = StringField('user_name', validators=[InputRequired()])
    name = StringField('name', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), Email()])
    password = StringField('password', validators=[InputRequired()])

    def validate_user(form, field):
        user = User.query.filter(User.user_name == form.user_name.data).first()
        if user is not None:
            raise ValidationError("A user with that username already exists")
