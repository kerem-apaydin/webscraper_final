from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .routes import main
from .scheduler_task import auto_scrape

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=auto_scrape, trigger="interval", minutes=60)

    scheduler.start()

    return app
