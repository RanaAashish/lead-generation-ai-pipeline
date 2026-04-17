from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Register the Blueprint
from app.routes import main as main_blueprint
app.register_blueprint(main_blueprint)
