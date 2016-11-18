from flask_wtf import Form
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired

'''
Add team members form. Requires user to select one or more usernames of members to add to the team.
Only the team admin can add members.'''
class EditTeamForm(Form):
    users = SelectMultipleField(u'Add Members', coerce=int, validators=[DataRequired()])

'''
Remove team members form. Requires user to select one or more usernames of members to remove
from the team. Only the team admin can remove members.'''
class RemoveMemberForm(Form):
    team_members = SelectMultipleField(u'Remove Members', coerce=int, validators=[DataRequired()])
