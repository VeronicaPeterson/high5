import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'z9y8x7w6v5u4t3s2r1'
WTF_CSRF_SECRET_KEY = 'z9y8x7w6v5u4t3s2r1'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'high5_app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


