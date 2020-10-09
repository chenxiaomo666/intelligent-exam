# coding:utf-8

from .. import db


class HistoryAnswer(db.Model):
    __tablename__ = 'history_answer'

    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer)
    submit_time = db.Column("submit_time", db.DateTime)
    exam_number = db.Column("exam_number", db.Integer)
    time_spent = db.Column("time_spend", db.Float)
    is_delete = db.Column("is_delete", db.Integer)
