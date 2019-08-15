from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
import sched
import threading
import time
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import os



viber = Api(BotConfiguration(
  name='JewleryNPBot',
  avatar='https://dl-media.viber.com/1/share/2/long/vibes/icon/image/0x0/69f8/2d81961fdd380df59e1cf921bc941da3337599b7e165a3f58417b5ba270a69f8.jpg',
  auth_token='4a1b33b858e7d578-e6ce7d64ca970f8e-8354ce174ff89d95'
))

db=SQLAlchemy()
migrate = Migrate()


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)

def set_webhook(viber):
    url = os.environ.get('URL') or \
       'https://a35b5edb.ngrok.io/'
    viber.set_webhook(url)

scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(7, 1, set_webhook, (viber,))
t = threading.Thread(target=scheduler.run)
t.start()



from bot import model, views
