from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

'''
Add team members form. Requires user to enter a comma-separated list of usernames of members to add to the team.
Only the team admin can add members.'''
class EditTeamForm(Form):
    users = StringField('users', validators=[DataRequired()])

'''
Remove team members form. Requires user to enter a comma-separated list of usernames of members to remove
from the team. Only the team admin can remove members.'''
class RemoveMemberForm(Form):
    team_members = StringField('team_members', validators=[DataRequired()])
