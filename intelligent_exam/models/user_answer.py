# coding:utf-8

from .. import db


class UserAnswer(db.Model):
    __tablename__ = 'user_answer'

    id = db.Column("id", db.Integer, primary_key=True)
    history_id = db.Column("history_id", db.Integer)
    user_id = db.Column("user_id", db.Integer)
    exam_number = db.Column("exam_number", db.Integer)
    subject_index = db.Column("subject_index", db.Integer)
    subject_content = db.Column("subject_content", db.Text)
    subject_choice = db.Column("subject_choice", db.Text)
    subject_answer = db.Column("subject_answer", db.Text)
    subject_type = db.Column("subject_type", db.Integer)
    user_answer = db.Column("user_answer", db.Text)
    time_spent = db.Column("time_spent", db.Float)
    answer_change = db.Column("choice_change", db.Text)
    submit_time = db.Column("submit_time", db.DateTime)
    is_delete = db.Column("is_delete", db.Integer)
