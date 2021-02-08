from flask import Blueprint, request
from ..repositorys.props import auth, success, error, panic
from ..models import Subject, UserAnswer, HistoryAnswer, User
from .. import db
from ..config import Config
from ..services.tool import base_query, func
import requests
import json
import random
from datetime import datetime

subject_view = Blueprint("subject_view", __name__)


# 录入试题，可根据具体的json格式录入，接受处理该请求
@subject_view.route("/subject/add", methods=["POST"])
@panic()
def subject_add():
    data = request.get_json()

    subject = Subject()
    subject.index = data["index"]
    subject.content = data["content"]
    subject.choice_content = data["choice_content"]
    subject.score = data["score"]
    subject.reference_answer = data["reference_answer"]
    subject.subject_type = data["subject_type"]
    subject.subject_number = data["subject_number"]
    subject.current_exam_number = data["exam_number"]
    subject.exist_exam_number = data["exist_exam_number"]

    db.session.add(subject)
    db.session.commit()
    
    return success()


# 根据exam_number和subject_index获取具体的试题
@subject_view.route("/subject/get", methods=["GET"])
@panic()
def subject_get():
    """
    data = {
        "exam_number" : 2021,
        "subject_index" : 14
    }
    """
    func()
    data = request.args
    
    if data.get("exam_number") is None:   # 随机抽取一套题
        _subject = base_query(Subject).first()
        if _subject is not None:
            exist_exam_number = _subject.exist_exam_number
            exam_number = 2009 + random.randint(1, exist_exam_number)   # 2010-2021，exist_exam_number=12
            subject_index = 1
        else:
            # 数据库中没有题
            return error(reason="数据库中未存放题目")
    else:
        try:
            exam_number = int(data.get("exam_number"))
            if exam_number<2010 or exam_number>2021:
                return error()
        except:
            return error()
        subject_index = 0   # 仅初始化，0无含义
        if data.get("subject_index") is None:   # 代表是按照年份抽取
            subject_index = 1
        else:
            subject_index = int(data.get("subject_index"))

    subject = base_query(Subject).filter_by(current_exam_number=exam_number, index=subject_index).first()
    if subject is None:
        return error(reason="试卷编号为{}已经到最后一题".format(exam_number))
    else:
        choice_content = []
        choice_content_str = subject.choice_content
        A_index = choice_content_str.index("A")
        B_index = choice_content_str.index("B")
        C_index = choice_content_str.index("C")
        D_index = choice_content_str.index("D")
        choice_content.append(choice_content_str[0:B_index])
        choice_content.append(choice_content_str[B_index:C_index])
        choice_content.append(choice_content_str[C_index:D_index])
        choice_content.append(choice_content_str[D_index:])
        result = {
                "index" : subject.index,
                "content" : subject.content,
                "choice_content" : choice_content,
                "score" : subject.score,
                "reference_answer" : subject.reference_answer,
                "subject_type" : subject.subject_type,
                "exam_number" : subject.current_exam_number,
                "subject_number" : subject.subject_number
            }
        return success({
            "result" : result
        })


# 用户点击试题提交，记录用户做题行为，并对数据进行处理存入数据库
@subject_view.route("/subject/submit", methods=["POST"])
@panic()
def subject_submit():
    
    data = request.get_json()
    user_info = data["user_info"]
    choice_list = data["choice_list"]
    
    history_answer = HistoryAnswer()
    history_answer.user_id = user_info["user_id"]
    history_answer.submit_time = datetime.now()
    history_answer.time_spent = data["time_spent"]
    history_answer.exam_number = data["exam_number"]
    db.session.add(history_answer)
    db.session.flush()
    history_id = history_answer.id

    for _choice in choice_list:

        user_answer = ""
        user_answer_temp = _choice["userAnswer"]
        if type(user_answer_temp) == str:
            user_answer = chr(64+int(user_answer_temp))
        elif type(user_answer_temp) == list:
            answer_str_list = []
            for x in user_answer_temp:
                answer_str_list.append(chr(64+int(x)))
            user_answer = "、".join(answer_str_list)

        answer_change = ""
        answer_change_temp = _choice["answerChange"]
        if answer_change_temp == None:
            answer_change = ""
        else:
            change_str_list = []
            for single_time in answer_change_temp:
                if type(single_time) == str:
                    change_str_list.append(chr(64+int(single_time)))
                elif type(single_time) == list:
                    _change_str_list = []
                    for x in single_time:
                        _change_str_list.append(chr(64+int(x)))
                    change_str_list.append("、".join(_change_str_list))
            answer_change = "->".join(change_str_list)
        
        subject_choice = _choice["subjectChoice"]
        if subject_choice == None:
            subject_choice_str = ""
        else:
            for i in range(len(subject_choice)):
                subject_choice[i] = subject_choice[i].strip(" \n")
            subject_choice_str = "|".join(subject_choice)
                
        _user_answer = UserAnswer()
        _user_answer.user_id = user_info["user_id"]
        _user_answer.history_id = history_id
        _user_answer.exam_number = data["exam_number"]
        _user_answer.subject_index = _choice["subjectIndex"]
        _user_answer.subject_content = _choice["subjectContent"]
        _user_answer.subject_choice = subject_choice_str
        _user_answer.subject_answer = _choice["subjectAnswer"]
        _user_answer.user_answer = user_answer
        _user_answer.time_spent = int(_choice["timeSpent"])/1000
        _user_answer.answer_change = answer_change
        _user_answer.submit_time = datetime.now()

        db.session.add(_user_answer)
    db.session.commit()

    return success({
        "history_id" : history_id
    })


# 获得用户具体某一次提交的内容，并返回处理好的信息
@subject_view.route("/subject/analysis", methods=["GET"])
@panic()
def subject_annlysis():
    history_id = request.args.get("history_id")
    history_answer = base_query(HistoryAnswer).filter_by(id=history_id).first()
    if history_answer is None:
        return error(reason="所查询用户提交历史答案不存在")
    else:
        user_id = history_answer.user_id
        exam_info = {
            "submit_time" : str(history_answer.submit_time),
            "exam_number" : history_answer.exam_number,
            "time_spent" : history_answer.time_spent,
        }

    user = base_query(User).filter_by(id=user_id).first()
    if user is None:
        user_info = {}
    else:
        user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }

    user_answers = base_query(UserAnswer).filter_by(history_id=history_id).all()
    
    user_answer_info = []
    current_subject_index = 1
    for _user_answer in user_answers:
        if _user_answer.subject_index is None:   # 代表它根本没看这个题就提交了
            exam_number = _user_answer.exam_number
            subject = base_query(Subject).filter_by(current_exam_number=exam_number, index=current_subject_index).first()
            if subject is None:
                user_answer_info.append({})   # 找不到该题目信息
            else:
                choice_content = []
                choice_content_str = subject.choice_content
                A_index = choice_content_str.index("A")
                B_index = choice_content_str.index("B")
                C_index = choice_content_str.index("C")
                D_index = choice_content_str.index("D")
                choice_content.append(choice_content_str[0:B_index])
                choice_content.append(choice_content_str[B_index:C_index])
                choice_content.append(choice_content_str[C_index:D_index])
                choice_content.append(choice_content_str[D_index:])
                
                user_answer_info.append({
                    "subject_index" : current_subject_index,
                    "subject_content" : subject.content,
                    "subject_choice_content" : choice_content,
                    "subject_reference_answer" : subject.reference_answer,
                    "subject_type" : subject.subject_type,
                    "user_answer" : _user_answer.user_answer,
                    "time_spent" : _user_answer.time_spent,
                    "answer_change" : _user_answer.answer_change
                })
        else:
            choice_content_str = _user_answer.subject_choice
            choice_content = choice_content_str.split("|")

            user_answer_info.append({
                "subject_index" : current_subject_index,
                "subject_content" : _user_answer.subject_content,
                "subject_choice_content" : choice_content,
                "subject_reference_answer" : _user_answer.subject_answer,
                "subject_type" : _user_answer.subject_type,
                "user_answer" : _user_answer.user_answer,
                "time_spent" : _user_answer.time_spent,
                "answer_change" : _user_answer.answer_change
            })

        current_subject_index += 1

    return success({
        "exam_info" : exam_info,
        "user_info" : user_info,
        "user_answer_info" : user_answer_info
    })


# 获取该user_id下的所有提交历史，做列表展示
@subject_view.route("/exam/history", methods=["GET"])
@panic()
def history_list():
    user_id = request.args.get("user_id")
    history_answers = base_query(HistoryAnswer).filter_by(user_id=user_id).all()

    user = base_query(User).filter_by(id=user_id).first()
    if user is None:
        user_info = {}
    else:
        user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }

    history_info = []
    for history_answer in history_answers:
        history_info.append({
            "submit_time" : str(history_answer.submit_time),
            "exam_number" : history_answer.exam_number,
            "time_spent" : history_answer.time_spent,
            "history_id" : history_answer.id,
        })

    return success({
        "user_info" : user_info,
        "history_info" : history_info
    })