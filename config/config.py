from collections import namedtuple

from os.path import join, dirname

dbpath = 'sqlite:///' + join(dirname(dirname(__file__)), 'data', 'app.db')

Config = namedtuple('Config', ('path', 'SQLALCHEMY_DATABASE_URI', 'SQLALCHEMY_TRACK_MODIFICATIONS'))(
    path=dbpath,
    SQLALCHEMY_DATABASE_URI=dbpath,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
