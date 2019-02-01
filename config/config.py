from collections import namedtuple

import os.path as path

dbpath = 'sqlite:///' + path.join(path.dirname(path.abspath('app.py')), 'data', 'app.db')

Config = namedtuple('Config', ('path', 'SQLALCHEMY_DATABASE_URI', 'SQLALCHEMY_TRACK_MODIFICATIONS'))(
    path=dbpath,
    SQLALCHEMY_DATABASE_URI=dbpath,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
