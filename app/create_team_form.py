from flask_wtf import Form
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired

'''
Create a new team form. Requires user to enter team name and allows them to select usernames of
members to add to the team. The team creator will be the team admin.'''
class TeamForm(Form):
    team_name = StringField('team_name', validators=[DataRequired()])
    team_members = SelectMultipleField(u'Team Members', coerce=int)