from flask_wtf import Form
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

'''
Create a new high5 form. Let the giver specify the receiver, the message, and a level of
helpfulness (1-5).'''
class High5Form(Form):
    receiver = StringField('receiver', validators=[DataRequired()])
    message = TextAreaField('message',  validators=[DataRequired()])
    level = IntegerField('level',  validators=[DataRequired()])