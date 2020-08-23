from flask import Flask
from config import config_data

app = Flask(__name__)
app.config.from_object('config')
for k,v in config_data.items():
    app.config[k] = v

from data_bike import routes