from flask_mail import Message
from app import mail
from flask import render_template
from config import ADMINS
from models import User

#Method to send an email to a list of recipients. The email has a subject and either a text body or html body.
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

#Method to specifically send a notification to the receiver of a new High5 to tell them they have received a high5.
#Uses a set subject and the admin email as the sender, but populates the message based on the giver and message.
def high5_notif(receiver, giver, message):
    send_email("%s gave you a High5!" % giver,
               ADMINS[0],
               [receiver.get_email()],
               render_template("high5_email.txt",
                               receiver=receiver, giver=giver, message=message),
               render_template("high5_email.html",
                               receiver=receiver, giver=giver, message=message))