import os

basedir = os.path.abspath(os.path.dirname('app.py'))


class Config:
    path = 'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    SQLALCHEMY_DATABASE_URI = path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
