from flask import render_template, redirect, url_for, g, flash
from sqlalchemy import desc
import datetime
from app import app, app_db, login_manager
from flask_login import login_required, login_user, logout_user, current_user
from models import User, Team, High5, calculate_score, calculate_top_scorers, \
    calculate_top_givers, calculate_top_receivers
from login_form import LoginForm, RegistrationForm
from create_team_form import TeamForm
from edit_team_form import EditTeamForm, RemoveMemberForm
from high5_form import High5Form
from edit_comment_form import EditCommentForm
from emails import high5_notif

"""Create the app routes used in the app URL. Login is the main team page. Any page which cannot be visited until a
user is logged in has the @login_required property."""

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

"""Create the login page for the app, which is the first page the user is brought to.
The login page has the login form and a button for the user to go to the registration page."""

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        user = LoginForm.validate_password(form, None)
        login_user(user)
        return redirect('/index/' + user_name)
    return render_template('login.html', form=form)

"""
Create the registration page for a new user. A user must fill in the registration form before they can be logged in.
If a user tries to register with an existing user name, they will be unable to register until they change the name."""
@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user_exists = User.query.filter(User.user_name == user_name).all()
        user_email_exists = User.query.filter(User.email == email).all()
        if not user_exists and not user_email_exists:
            new_user = User(user_name, name, email, password)
            app_db.session.add(new_user)
            app_db.session.commit()
            login_user(new_user)
            return redirect('/index/' + user_name)
    return render_template('registration.html', form=form)

"""
Logout the currently logged in user and bring the user to the login page."""
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

"""Create the index page, which is the first page the user sees after login. This page has a list
of all the user's teams in alphabetical order so a user can select which team to view.
Also has a form for a user to create a new team with a team name and starting members."""

@app.route('/index/<user_name>', methods=['GET', 'POST'])
@login_required
def index(user_name):
    teams = Team.query.filter(Team.members.any(User.user_name == user_name)).order_by(Team.name).all()
    form = TeamForm()
    if form.validate_on_submit():
        team_name = form.team_name.data
        team_members = [x.strip() for x in form.team_members.data.split(',')]
        team_members.append(user_name)
        list(set(team_members))
        new_team = Team(name=team_name, admin=user_name)
        for team_member in team_members:
            user1 = User.query.filter(User.user_name == team_member).one()
            if user1:
                new_team.members.append(user1)
        app_db.session.add(new_team)
        app_db.session.commit()
        return redirect('/index/' + user_name)
    return render_template('index.html', teams=teams, user=user_name, form=form)


"""Create the team page, which is specific for the user and selected team from index page.
The team page shows the top high5 scorers and givers, as well as a list of all high5's given for the team starting with
the most recent. If the current user is the admin of the team, then they will be able to
select "Edit Team" to go to the edit team page."""

@app.route('/team/<user_name>/<team_name>', methods=['GET', 'POST'])
@login_required
def team(team_name, user_name):
    team = Team.query.get(team_name)
    high5s = High5.query.filter(High5.team_name == team_name).order_by(desc(High5.time_posted)).all()
    team_members = team.members.all()
    top_scorers = calculate_top_scorers(high5s, team_members)
    top_receivers = calculate_top_receivers(high5s, team_members)
    top_givers = calculate_top_givers(high5s, team_members)
    return render_template('team.html', team=team, user=user_name, high5s=high5s,
                           top_receivers=top_receivers, top_scorers=top_scorers, top_givers=top_givers)


"""Create the page for a user to give high5's to other teammates on the selected team. Add the new High5 to the db."""

@app.route('/giveHigh5/<user_name>/<team_name>', methods=['GET', 'POST'])
@login_required
def giveHigh5(team_name, user_name):
    team = Team.query.get(team_name)
    form = High5Form()
    if form.validate_on_submit():
        receiver = form.receiver.data
        message = form.message.data
        level = form.level.data
        if level < 1:
            level = 1
        elif level > 5:
            level = 5
        else:
            level = level
        new_high5 = High5(receiver=receiver, giver=user_name, message=message, time_posted=datetime.datetime.utcnow(),
                          level=level, team=team)
        app_db.session.add(new_high5)
        app_db.session.commit()
        return redirect('/notify/' + user_name + '/' + team_name + '/' + receiver + '/' + message)
    return render_template('giveHigh5.html', team=team, user=user_name, form=form)

"""Send an email notification to the receiver of a new High5. Gets called from the GiveHigh5 page and sends an email from
 the admin account to the receiver with the giver's name and contents of the message. Returns the user who gave the
 high5 to the team page."""

@app.route('/notify/<user_name>/<team_name>/<receiver_name>/<message>', methods=['GET', 'POST'])
@login_required
def follow(user_name, team_name, receiver_name, message):
    receiver = User.query.filter(User.user_name == receiver_name).first()
    high5_notif(receiver, user_name, message)
    return redirect('/team/' + user_name + '/' + team_name)

"""Create the user page, specific to the user and the selected team. Show the user's total
high5 score and all received high5's starting with the most recent. Also list the high5's that a user has given and
allow the user to edit any of those high5's."""

@app.route('/user/<user_name>/<team_name>', methods=['GET', 'POST'])
@login_required
def user(team_name, user_name):
    team = Team.query.get(team_name)
    high5s = High5.query.filter(High5.team_name == team_name).filter(High5.receiver == user_name). \
        order_by(desc(High5.time_posted)).all()
    score = calculate_score(high5s)
    myhigh5s = High5.query.filter(High5.team_name == team_name).filter(High5.giver == user_name). \
        order_by(desc(High5.time_posted)).all()
    return render_template('user.html', team=team, user=user_name, high5s=high5s, score=score, myhigh5s=myhigh5s)


"""Create the page for a team admin to edit a team by by adding/removing team members.
This page can only be reached by the admin of the team. Any added users must exist in the Users table and cannot
already exist in the team. Two forms exist for adding or removing members multiple at a time. If a user is removed from
a team, the team page no longer includes any High5's that member received. This page also
has the button for a user to delete a team. """

@app.route('/edit/<user_name>/<team_name>', methods=['GET', 'POST'])
@login_required
def editTeam(team_name, user_name):
    team = Team.query.get(team_name)
    if not team.get_admin() == user_name:
        return redirect('/team/' + user_name + '/' + team_name)
    members = team.members.all()
    edit_form = EditTeamForm()
    remove_member_form = RemoveMemberForm()
    if edit_form.validate_on_submit():
        team_members = [x.strip() for x in edit_form.users.data.split(',')]
        list(set(team_members))
        for team_member in team_members:
            user1 = User.query.filter(User.user_name == team_member).first()
            if user1 and user1 not in members:
                team.members.append(user1)
        app_db.session.commit()
        return redirect('/edit/' + user_name + '/' + team_name)
    if remove_member_form.validate_on_submit():
        team_members = [x.strip() for x in remove_member_form.team_members.data.split(',')]
        list(set(team_members))
        for team_member in team_members:
            if not (team_member == user_name):
                user1 = User.query.filter(User.user_name == team_member).first()
                if user1:
                    team.members.remove(user1)
                    High5.query.filter(High5.team_name==team_name).filter(High5.receiver==team_member).delete()
        app_db.session.commit()
        return redirect('/edit/' + user_name + '/' + team_name)
    return render_template('editTeam.html', team=team, user=user_name, members=members,
                           edit_form=edit_form, remove_member_form=remove_member_form)

"""Create the page for a team admin to delete a team which they are the admin for. Only allow an admin to delete a team.
Bring the user back to the Teams page after deleting."""

@app.route('/delete/<user_name>/<team_name>', methods=['GET', 'POST'])
@login_required
def deleteTeam(team_name, user_name):
    team = Team.query.get(team_name)
    if not team.get_admin() == user_name:
        return redirect('/team/' + user_name + '/' + team_name)
    app_db.session.delete(team)
    app_db.session.commit()
    return redirect('/index/' + user_name)

"""Create the page for a user to edit the message of a High5 that they have given. Only allow a user to edit the message
of a High5 that they have given. Update the message in the db and return the user to their user page. This page
also has the button for a user to delete a High5. """

@app.route('/editHigh5/<user_name>/<team_name>/<id>', methods=['GET', 'POST'])
@login_required
def editHigh5(team_name, user_name, id):
    high5 = High5.query.get(id)
    if not high5.get_giver() == user_name:
        return redirect('/user/' + user_name + '/' + team_name)
    edit_form = EditCommentForm()
    if edit_form.validate_on_submit():
        new_message = edit_form.comment_update.data
        setattr(high5, 'message', new_message)
        app_db.session.commit()
        return redirect('/user/' + user_name + '/' + team_name)
    return render_template('editComment.html', team=team_name, user=user_name, high5=high5, edit_form=edit_form)

"""Create the page for a user to delete a High5 that they have given. Only can the giver of a High5 delete it. Bring the
user back to their user page after deleting the High5."""

@app.route('/deleteHigh5/<user_name>/<team_name>/<id>', methods=['GET', 'POST'])
@login_required
def deleteHigh5(team_name, user_name, id):
    high5 = High5.query.get(id)
    if not high5.get_giver() == user_name:
        return redirect('/user/' + user_name + '/' + team_name)
    app_db.session.delete(high5)
    app_db.session.commit()
    return redirect('/user/' + user_name + '/' + team_name)