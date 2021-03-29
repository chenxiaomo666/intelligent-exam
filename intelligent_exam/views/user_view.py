from flask import Blueprint, request, render_template
from ..repositorys.props import auth, success, error, panic
from ..models import User, Room
from .. import db
from ..config import Config
from ..services.tool import base_query, login, get_empty_class_room
from datetime import datetime
import requests
import json
import csv

user_view = Blueprint("user_view", __name__)


# 增加新用户，实现user_id与微信号一一绑定
@user_view.route("/user/add", methods=["POST"])
@panic()
def user_add():
    user_data = request.get_json()
    user = base_query(User).filter_by(openid=user_data['openid']).first()
    if user is None:
        user = User()
    user.true_name = user_data["true_name"]
    user.openid = user_data["openid"]
    user.nickname = user_data["nickname"]
    user.head_img = user_data["head_img"]
    user.sex = user_data["sex"]
    user.school_ID = user_data["school_ID"]
    user.school_name = user_data["school_name"]
    user.is_teacher = user_data["is_teacher"]

    db.session.add(user)
    db.session.commit()

    user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }

    return success({
        "user_info": user_info
    })


# 查询微信用户是否在本数据库中进行过绑定
@user_view.route("/user/query", methods=["GET"])
@panic()
def user_query():
    data = dict(request.args)
    data.update({
        "appid": Config.APPID,
        "secret": Config.SECRET,
    })

    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = data

    response = requests.get(url=url, params=params)
    user_data = json.loads(response.text)

    user_openid = user_data['openid']

    user = base_query(User).filter_by(openid=user_openid).first()
    if user is not None:
        is_bind = True
        user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user_openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }
    else:
        is_bind = False
        user_info = {
            "openid": user_openid
        }

    return success({
        "is_bind": is_bind,
        "user_info": user_info
    })


# 获取全部学生列表，展示学生信息
@user_view.route("/student/list", methods=["GET"])
@panic()
def get_all_student():
    students = base_query(User).filter_by(is_teacher=0).all()
    
    student_list = []

    for user in students:
        student_list.append({
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "school_ID": user.school_ID,
        })

    return success({
        "student_list" : student_list
    })


# 用户身份由教师更改为学生（方便测试）
@user_view.route("/change/student", methods=["post"])
@panic()
def change_student():
    data = request.get_json()
    user_id = data["user_id"]
    
    user = base_query(User).filter_by(id=user_id).first()
    if user is None:
        return error("无法定位到该用户信息")
    else:

        user.is_teacher = 0
        
        db.session.flush()

        user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }

        db.session.commit()

        return success({
            "user_info" : user_info
        })


# 用户身份由学生更改为教师（方便测试）
@user_view.route("/change/teacher", methods=["post"])
@panic()
def change_teacher():
    data = request.get_json()
    user_id = data["user_id"]
    
    user = base_query(User).filter_by(id=user_id).first()
    if user is None:
        return error("无法定位到该用户信息")
    else:
        user.is_teacher = 1
        
        db.session.flush()

        user_info = {
            "user_id": user.id,
            "true_name": user.true_name,
            "openid": user.openid,
            "nickname": user.nickname,
            "head_img": user.head_img,
            "is_teacher": user.is_teacher
        }

        db.session.commit()

        return success({
            "user_info" : user_info
        })
    

# 空教室查询
@user_view.route("/emptyroom", methods=["get"])
@panic()
def empty_room():

    is_first = False
    frequency = 0

    kaoyan_time = datetime(Config.KAOYAN_TIME[0], Config.KAOYAN_TIME[1], Config.KAOYAN_TIME[2])    # 21年考研日期，婷婷
    now_time = datetime.now()
    countdown = (kaoyan_time - now_time).days + 1
    # now_time = datetime(2020, 9, 13)
    # room = base_query(Room).filter_by(author="cxm").first()
    room = base_query(Room).order_by(Room.id.desc()).first()
    
    if room is not None:
        time = room.time
        frequency = room.frequency + 1
        if time.year==now_time.year and time.month==now_time.month and time.day==now_time.day:   # 代表今天的数据已经有了
            is_first = False
            room.frequency = frequency
            all = room.all
            morning = room.morning
            afternoon = room.afternoon
            evening = room.evening
            one_two = room.one_two
            three_four = room.three_four
            five_six = room.five_six
            seven_eight = room.seven_eight
            nine_ten = room.nine_ten
        else:
            is_first = True
            room = Room()    # 每天的数据都保留着
            frequency = 1
            login()
            all, morning, afternoon, evening, one_two, three_four, five_six, seven_eight, nine_ten = get_empty_class_room()
            room.time = now_time
            room.all = all
            room.morning = morning
            room.afternoon = afternoon
            room.evening = evening
            room.frequency = frequency
            room.one_two = one_two
            room.three_four = three_four
            room.five_six = five_six
            room.seven_eight = seven_eight
            room.nine_ten = nine_ten
            db.session.add(room)
    else:
        is_first = True
        frequency = 1
        login()
        all, morning, afternoon, evening, one_two, three_four, five_six, seven_eight, nine_ten = get_empty_class_room()
        room = Room()
        room.time = now_time
        room.all = all
        room.morning = morning
        room.afternoon = afternoon
        room.evening = evening
        room.one_two = one_two
        room.three_four = three_four
        room.five_six = five_six
        room.seven_eight = seven_eight
        room.nine_ten = nine_ten
        room.author = "cxm"
        room.frequency = 1
        db.session.add(room)
        
    weekday_ = now_time.weekday()+1
    week_dict = {1:"一", 2:"二", 3:"三", 4:"四", 5:"五", 6:"六", 7:"日"}
    weekday = week_dict[weekday_]
    db.session.commit()

    result = {
        "weekday": weekday,
        "time": str(now_time)[:10],
        "all" : all,
        "morning":  morning,
        "afternoon":  afternoon,
        "evening": evening,
        "one_two" : one_two,
        "three_four":  three_four,
        "five_six":  five_six,
        "seven_eight": seven_eight,
        "nine_ten": nine_ten,
        "is_first": is_first,
        "frequency": frequency,
        "countdown": countdown
    }

    return success({
        "result": result
    })