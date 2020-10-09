from .. import db, app
from .user import User
from .room import Room
from .subject import Subject
from .user_answer import UserAnswer
from .history_answer import HistoryAnswer


def init_model():
    db.create_all(app=app)