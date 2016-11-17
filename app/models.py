from app import app_db
import operator
from random import SystemRandom

from backports.pbkdf2 import pbkdf2_hmac, compare_digest
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

'''
Database table members to represent the many to many relationship between Teams and Users.
A user can be on many teams and a team can have many users. Each user can only
be on a team one time. Uses the primary keys of the Team and User tables.'''
members = app_db.Table('members',
                app_db.Column('team', app_db.String(100), app_db.ForeignKey('team.name', ondelete='CASCADE')),
                app_db.Column('user', app_db.Integer, app_db.ForeignKey('user.id', ondelete='CASCADE')),
                app_db.UniqueConstraint('team', 'user', name='UC_team_user')
                )

'''
Class to represent a User on the High5 website in the database. In the db, a user has a unique  given id,
a unique chosen user_name, a name, an email, and a password for login. The user can be a part of
multiple Teams through a relationship in the members table. The password for the User must be stored hashed
so that there is security around it.'''
class User(UserMixin, app_db.Model):
    id = app_db.Column(app_db.Integer, primary_key=True)
    user_name = app_db.Column(app_db.String(50), unique=True)
    name = app_db.Column(app_db.String(50), index=True)
    email = app_db.Column(app_db.String(120), unique=True)
    _password = app_db.Column(app_db.LargeBinary(120))
    _salt = app_db.Column(app_db.String(120))

    def __init__(self , user_name ,name , email, password):
        self.user_name = user_name
        self.name = name
        self.email = email
        self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(password)

    #Print representation of a User for testing
    def __repr__(self):
        return '<User %r>' % (self.user_name)

    #Getter for the User unique id, necessary for flask-login
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    #Getter for the User user name
    def get_user_name(self):
        return self.user_name

    #Getter for the User name
    def get_name(self):
        return self.name

    #Getter for the User email
    def get_email(self):
        return self.email

    #Getter for the hashed password.
    @hybrid_property
    def password(self):
        return self._password

    #Method to check if the given password is valid.
    def is_valid_password(self, password):
        new_hash = self._hash_password(password)
        return compare_digest(new_hash, self._password)

    #Method to hash a password.
    def _hash_password(self, password):
        pwd = password.encode("utf-8")
        salt = bytes(self._salt)
        buff = pbkdf2_hmac("sha512", pwd, salt, iterations=100000)
        return bytes(buff)

'''
Class to represent a Team on the High5 website in the database. In the db, a team has a name, an admin which is
represented by the username of an existing user, and relationships with users and high5s. A team can have many users and
also many High5's.'''
class Team(app_db.Model):
    name = app_db.Column(app_db.String(100), primary_key=True)
    admin = app_db.Column(app_db.String(50), app_db.ForeignKey('user.user_name', ondelete='CASCADE'))
    high5s = app_db.relationship('High5', backref='team', lazy='dynamic', cascade="all, delete-orphan")
    members = app_db.relationship('User', secondary=members, backref=app_db.backref('teams', lazy='dynamic'), lazy='dynamic')

    #Print representation of team for testing
    def __repr__(self):
        return '<Team %r>' % (self.name)

    #Getter for the team name
    def get_name(self):
        return self.name

    #Getter for the team admin
    def get_admin(self):
        return self.admin


'''
High5 is a class to represent the High5 messages team members can give to each other on the website.
In the database, High5's have a unique id, a receiver and a giver which are both User's usernames, a message, a
time the High5 was posted, and a level between 1 and 5 of the helpfulness of a contribution.
A High5 also knows what team it is a part of because a High5 is the many side of the one to many
relationship with a Team (a High5 can only belong to one team).'''
class High5(app_db.Model):
    id = app_db.Column(app_db.Integer, primary_key = True)
    receiver = app_db.Column(app_db.String(50), app_db.ForeignKey('user.user_name', ondelete='CASCADE'))
    giver = app_db.Column(app_db.String(50), app_db.ForeignKey('user.user_name', ondelete='CASCADE'))
    message = app_db.Column(app_db.String(250))
    time_posted = app_db.Column(app_db.DateTime)
    level = app_db.Column(app_db.Integer)
    team_name = app_db.Column(app_db.String(100), app_db.ForeignKey('team.name', ondelete='CASCADE'))

    #Print representation of a High5 for testing
    def __repr__(self):
        return '<High5 %r>' % (self.message)

    #Getter for the High5 receiver
    def get_receiver(self):
        return self.receiver

    #Getter for the High5 giver
    def get_giver(self):
        return self.giver

    #Getter for the High5 message
    def get_message(self):
        return self.message

    #Getter for the High5 formatted date time
    def get_time(self):
        return self.time_posted.strftime("%Y-%m-%d %H:%M")

    #Getter for the High5 level
    def get_level(self):
        return self.level

#Calculate the high5 score based on the passed in list of high5s, which will be all the High5's
#received by one team member (the current user).
def calculate_score(high5s):
    score = 0
    for high5 in high5s:
        score += high5.get_level()
    return score

#Get the top three high5 scorers on the team. Go through team members and find their high5 scores.
#Return up to 3 of the top scores with name and score.
def calculate_top_scorers(high5s, members):
    member_scores = {}
    for member in members:
        score = 0
        for high5 in high5s:
            if high5.get_receiver() == member.get_user_name():
                score += high5.get_level()
        member_scores[member.get_user_name()] = score
    member_scores_pairs = []
    for key,value in member_scores.iteritems():
        member_scores_pairs.append((key, value))
    sorted_scores = sorted(member_scores_pairs, key=operator.itemgetter(1))
    sorted_scores.reverse()
    if len(sorted_scores) > 2:
        return sorted_scores[:3]
    elif len(sorted_scores) > 1:
        return sorted_scores[:2]
    elif len(sorted_scores) > 0:
        return sorted_scores[:1]
    else:
        return None

#Get the top three high5 members with most high5's by count on the team.
#Go through team members and find the count of their high5's.
#Return up to 3 of the top earners with name and count.
def calculate_top_receivers(high5s, members):
    member_counts = {}
    for member in members:
        count = 0
        for high5 in high5s:
            if high5.get_receiver() == member.get_user_name():
                count += 1
        member_counts[member.get_user_name()] = count
    member_count_pairs = []
    for key,value in member_counts.iteritems():
        member_count_pairs.append((key, value))
    sorted_counts = sorted(member_count_pairs, key=operator.itemgetter(1))
    sorted_counts.reverse()
    if len(sorted_counts) > 2:
        return sorted_counts[:3]
    elif len(sorted_counts) > 1:
        return sorted_counts[:2]
    elif len(sorted_counts) > 0:
        return sorted_counts[:1]
    else:
        return None

#Get the top three high5 members who gave the most high5's by count on the team.
#Go through team members and find the count of their given high5's.
#Return up to 3 of the top earners with name and count.
def calculate_top_givers(high5s, members):
    member_counts = {}
    for member in members:
        count = 0
        for high5 in high5s:
            if high5.get_giver() == member.get_user_name():
                count += 1
        member_counts[member.get_user_name()] = count
    member_count_pairs = []
    for key,value in member_counts.iteritems():
        member_count_pairs.append((key, value))
    sorted_counts = sorted(member_count_pairs, key=operator.itemgetter(1))
    sorted_counts.reverse()
    if len(sorted_counts) > 2:
        return sorted_counts[:3]
    elif len(sorted_counts) > 1:
        return sorted_counts[:2]
    elif len(sorted_counts) > 0:
        return sorted_counts[:1]
    else:
        return None


