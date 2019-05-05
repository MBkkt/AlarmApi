from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from os import path, mkdir

app = Flask(__name__)
app.config.from_object(Config)
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'],
            subject='Alarm api Failure',
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not path.exists('logs'):
        mkdir('logs')
    file_handler = RotatingFileHandler('logs/server.log')
    file_handler.setFormatter(
        logging.Formatter(
            '{asctime} {levelname}: {message} [in {pathname}:{lineno}',
            style='{')
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Alalrm Api startup')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes
