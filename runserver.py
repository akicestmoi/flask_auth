from flask import Flask
from api import create_app, db
from config import Config
from flask_migrate import Migrate

app: Flask = create_app(Config)
migrate: Migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
else:
    gunicorn_app = create_app(Config)