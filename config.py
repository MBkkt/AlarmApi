from collections import namedtuple
from os import path, environ, mkdir

basedir = path.abspath(path.dirname(__file__))
if not path.exists('data'):
    mkdir('data')

Config = namedtuple('Config', (
    'path', 'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI',
    'SQLALCHEMY_TRACK_MODIFICATIONS', 'MAIL_SERVER', 'MAIL_PORT',
    'MAIL_USE_TLS', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'ADMINS',))(
    path=basedir,
    SECRET_KEY=(
            environ.get('SECRET_KEY')
            or 'you-will-never-guess'
    ),
    SQLALCHEMY_DATABASE_URI=(
            environ.get('DATABASE_URL') or
            'sqlite:///' + path.join(basedir, 'data', 'app.db')
    ),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAIL_SERVER=environ.get('MAIL_SERVER'),
    MAIL_PORT=int(environ.get('MAIL_PORT') or 25),
    MAIL_USE_TLS=environ.get('MAIL_USE_TLS') is not None,
    MAIL_USERNAME=environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=environ.get('MAIL_PASSWORD'),
    ADMINS=['your-email@example.com'],
)
