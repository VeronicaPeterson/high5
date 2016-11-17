import unittest
import os
import sys
sys.path.append('..')
from app import app_db
import datetime
from app.models import User, Team, High5, calculate_score

"""
Class to test tthe team and user classes and that the methods function properly to update both.
"""
class MyDBTest(unittest.TestCase):
    #Function to setup for the rest of the tests.
    def setUp(self):
        super(MyDBTest, self).setUp()
        exists = Team.query.get("Men's Running Club Test")
        if exists:
            app_db.session.delete(exists)
            app_db.session.commit()
        user_exists = User.query.filter(User.user_name == "Jimmy").first()
        if user_exists:
            app_db.session.delete(user_exists)
            app_db.session.commit()

#Tests for adding and removing a team from the db.
    def test_add_remove_team(self):
        new_team = Team(name="Men's Running Club Test", admin="VPeterson")
        team_members = []
        team_members.append("John")
        team_members.append("Tom")
        list(set(team_members))
        for team_member in team_members:
            user1 = User.query.filter(User.user_name == team_member).one()
            if user1:
                new_team.members.append(user1)
        app_db.session.add(new_team)
        app_db.session.commit()
        team_exists = Team.query.filter(Team.name == "Men's Running Club Test").all()
        self.assertEqual(len(team_exists), 1)
        app_db.session.delete(new_team)
        app_db.session.commit()
        team_exists = Team.query.filter(Team.name == "Men's Running Club Test").all()
        self.assertEqual(len(team_exists), 0)

    #Tests for adding and removing a user from the db. Make sure the email, username, and name are stored correctly.
    #Test that the password is stored hashed and cannot be retrieved.
    def test_add_remove_user(self):
        new_user = User(user_name='Jimmy', name='Jimmy John', email='jjohn@illinois.edu', password='jjjj')
        app_db.session.add(new_user)
        app_db.session.commit()
        user_exists = User.query.filter(User.user_name == "Jimmy").all()
        self.assertEqual(len(user_exists), 1)
        self.assertEqual(user_exists[0].get_email(), "jjohn@illinois.edu")
        self.assertEqual(user_exists[0].get_name(), "Jimmy John")
        self.assertNotEqual(user_exists[0].password, "jjjj")
        app_db.session.delete(new_user)
        app_db.session.commit()
        user_exists = User.query.filter(User.user_name == "Jimmy").all()
        self.assertEqual(len(user_exists), 0)

    #Tests for adding a user, a team, and high5s for that team. Tests that the high5s are added. Tests that if
    #you remove a member, any high5's that that user has received are deleted. Tests that deleting a team deletes all
    #high5s for that team.
    def test_add_high5s(self):
        new_user = User(user_name='Jimmy', name='Jimmy John', email='jjohn@illinois.edu', password='jjjj')
        app_db.session.add(new_user)
        app_db.session.commit()
        new_team = Team(name="Men's Running Club Test", admin="Jimmy")
        team_members = []
        team_members.append("John")
        team_members.append("Tom")
        list(set(team_members))
        for team_member in team_members:
            user1 = User.query.filter(User.user_name == team_member).one()
            if user1:
                new_team.members.append(user1)
        app_db.session.add(new_team)
        high5_1 = High5(receiver='Tom', giver='Jimmy', message='Tom went in to extra office hours to get feedback on our project change idea', time_posted=datetime.datetime.utcnow(), level=5, team=new_team)
        high5_2 = High5(receiver='John', giver='Tom', message='John went to the store to get supplies to make paper prototypes.', time_posted=datetime.datetime.utcnow(), level=4, team=new_team)
        app_db.session.add(high5_1)
        app_db.session.add(high5_2)
        app_db.session.commit()
        high5s = High5.query.filter(High5.team_name == "Men's Running Club Test").all()
        self.assertEqual(len(high5s), 2)
        john = User.query.filter(User.user_name == "John").one()
        new_team.members.remove(john)
        High5.query.filter(High5.team_name=="Men's Running Club Test").filter(High5.receiver=="John").delete()
        app_db.session.commit()
        high5s = High5.query.filter(High5.team_name == "Men's Running Club Test").all()
        self.assertEqual(len(high5s), 1)
        app_db.session.delete(new_team)
        app_db.session.delete(new_user)
        app_db.session.commit()
        team_exists = Team.query.filter(Team.name == "Men's Running Club Test").all()
        self.assertEqual(len(team_exists), 0)
        high5s = High5.query.filter(High5.team_name == "Men's Running Club Test").all()
        self.assertEqual(len(high5s), 0)

    def test_calculate_score(self):
        new_team = Team(name="Men's Running Club Test", admin="Jimmy")
        high5_1 = High5(receiver='Tom', giver='Jimmy', message='Tom went in to extra office hours to get feedback on our project change idea', time_posted=datetime.datetime.utcnow(), level=5, team=new_team)
        high5_3 = High5(receiver='Tom', giver='Jimmy', message='Tom went in to extra office hours to get feedback on our project change idea', time_posted=datetime.datetime.utcnow(), level=1, team=new_team)
        tom_high5s = []
        tom_high5s.append(high5_1)
        tom_high5s.append(high5_3)
        self.assertEqual(calculate_score(tom_high5s), 6)



if __name__ == '__main__':
    unittest.main()