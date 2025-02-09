from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = Flask(__name__)
db = SQLAlchemy()
socketio = SocketIO(app)
