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
import sys



viber = Api(BotConfiguration(
  name='JuliasAssistant',
  avatar='https://i.ibb.co/vc2gJBZ/logo.jpg',
  auth_token='4a1b33b858e7d578-e6ce7d64ca970f8e-8354ce174ff89d95'
))

db=SQLAlchemy()
migrate = Migrate()


app = Flask(__name__)
app.config.from_object(Config)
migrate.init_app(app, db)

def set_webhook(viber):
    try:
        url = os.environ.get('URL') or \
           'https://ac67ee8a.ngrok.io/'
        viber.set_webhook(url)
    except:
        print(sys.exc_info())
scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(7, 1, set_webhook, (viber,))
t = threading.Thread(target=scheduler.run)
t.start()



from bot import model, views
