# coding:utf-8

from .. import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column("id", db.Integer, primary_key=True)
    true_name = db.Column("true_name", db.String(64))
    openid = db.Column("openid", db.String(64))
    nickname = db.Column("nickname", db.String(64))
    head_img = db.Column("head_img", db.String(500))
    sex = db.Column("sex", db.Integer)     # 0：女生，1：男生
    school_ID = db.Column("school_ID", db.Integer)
    school_name = db.Column("school_name", db.String(64))
    is_teacher = db.Column("is_teacher", db.Integer)   # 0：否，1：是
    is_delete = db.Column("is_delete", db.Integer)
