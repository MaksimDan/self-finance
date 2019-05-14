from flask import Flask
from flask_bootstrap import Bootstrap

from config.files import dirs
from self_finance.constants import App

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = App.SECRET_KEY
app._static_folder = dirs['static']

from self_finance.front_end.routes import index, data, insights, visuals, settings, reference
from self_finance.front_end.routes import errors
