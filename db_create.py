#!flask/bin/python
#from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import app_db
from app import db_add_team
import os

#Delete the database if it already exists
os.system('rm high5_app.db')

#Create the database and fill it with made up users and teams initially.
app_db.create_all()
db_add_team.create_users()
db_add_team.create_running_team()
db_add_team.create_project_team()

# if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
#     api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# else:
#     api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))