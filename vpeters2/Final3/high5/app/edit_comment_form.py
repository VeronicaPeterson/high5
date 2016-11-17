from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

'''
Edit the message of a High5. A message can only be edited by the user who gave the High5. Allows the user
to write completely new message to replace the existing.'''
class EditCommentForm(Form):
    comment_update = StringField('commment_update', validators=[DataRequired()])


