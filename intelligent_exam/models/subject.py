# coding:utf-8

from .. import db


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column("id", db.Integer, primary_key=True)
    index = db.Column("index", db.Integer)   # 题目编号
    content = db.Column("content", db.Text)  # 题目内容
    choice_content = db.Column("choice_content", db.Text)   # 如果是选择题，存储选择题选项
    score = db.Column("score", db.Integer)    # 当前题目分数
    reference_answer = db.Column("reference_answer", db.Text)  # 参考答案
    subject_type = db.Column("subject_type", db.Integer)   # 0：单项选择，1：多项选择
    current_exam_number = db.Column("exam_number", db.Integer)   # 题目所属试卷编号
    subject_number = db.Column("subject_number", db.Integer)    # 本试卷一共有多少道题
    exist_exam_number = db.Column("exist_exam_number", db.Integer)
    is_delete = db.Column("is_delete", db.Integer)
