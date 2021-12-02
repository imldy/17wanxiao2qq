from datetime import date, datetime, timezone, timedelta

import requests
import json
import sys
import yaml


class Task():
    def __init__(self, id, name, remind_text):
        self.id = id
        self.name = name
        self.remind_text = remind_text


class Student():
    def __init__(self, id, name, qq, ignore):
        self.id = id
        self.name = name
        self.qq = qq
        if ignore == 0:
            self.ignore = False
        else:
            self.ignore = True


class WanXiao():
    def __init__(self, username, passward):
        self.wx_root_url = "https://reported.17wanxiao.com/"
        self.username = username
        self.passward = passward
        self.session = requests.session()

    def login(self):
        # 请求登录页面，获取一些cookie
        self.session.get("https://reported.17wanxiao.com/login.html")
        # 请求验证码图片，获取一些cookie，实际一段时间内第一次登录用不到输入验证码
        self.session.get("https://reported.17wanxiao.com/captcha.jpg?t=13")
        login_url = "{}admin/login".format(self.wx_root_url)
        data = {
            "username": self.username,
            "securitycode": self.passward
        }
        resp = self.session.post(login_url, data=data)
        # print(resp.text)
        if resp.status_code == 200:
            return True
        return False

    def get_no_check_stu_list(self):
        url = "https://reported.17wanxiao.com/student/list2"
        args = {
            "deptId": "",
            "undo": 0,
            "reportTime": "",
            "_search": "false",
            # "nd": 1631956327043,  # 截至时间
            "limit": 300,
            "page": 1,
            "sidx": "",
            "order": "asc",
            # "_": 1631956326256
        }
        resp = self.session.get(url, params=args)
        # print(resp.text)
        if '"result":true,' in resp.text:
            resp_dict = resp.json()
            no_check_stu_list = []
            for record in resp_dict["page"]["records"]:
                no_check_stu_list.append(Student(record["stuNo"], record["name"], None, 0))
            return no_check_stu_list
        else:
            print("获取失败")
        # return [Student(), Student()]


class QQBot():
    def __init__(self, root_url, verify_key, dest_group_no, bot_qq):
        self.root_url = root_url
        self.verify_key = verify_key
        self.session_key = ""
        self.dest_group_no = dest_group_no
        self.bot_qq = bot_qq

    def verify(self):
        '''
        使用此方法验证你的身份，并返回一个会话(session_key)
        :return:
        '''
        data = {
            "verifyKey": self.verify_key
        }
        resp = requests.post("{}/verify".format(self.root_url), json=data)
        session_key = json.loads(resp.text)["session"]
        self.session_key = session_key
        return session_key

    def bind(self):
        '''
        使用此方法校验并激活你的Session，同时将Session与一个已登录的Bot绑定
        :param session_key:
        :param qq:
        :return:
        '''
        data = {
            "sessionKey": self.session_key,
            "qq": self.bot_qq
        }
        resp = requests.post("{}/bind".format(self.root_url), json=data)
        msg = json.loads(resp.text)["msg"]
        return msg

    def release(self):
        '''
        放session及其相关资源（Bot不会被释放） 不使用的Session应当被释放
        长时间（30分钟）未使用的Session将自动释放，否则Session持续保存Bot收到的消息，将会导致内存泄露(开启websocket后将不会自动释放)
        :param session_key:
        :param qq:
        :return:
        '''
        data = {
            "sessionKey": self.session_key,
            "qq": self.bot_qq
        }
        resp = requests.post("{}/release".format(self.root_url), json=data)
        msg = json.loads(resp.text)["msg"]
        return msg

    def send_temp_session_message(self, dest_qq, group, messageChain):
        data = {
            "sessionKey": self.session_key,
            "qq": dest_qq,
            "group": group,
            "messageChain": messageChain
        }
        resp = requests.post("{}/sendTempMessage".format(self.root_url), json=data)
        msg = json.loads(resp.text)["msg"]
        return msg

    def send_friend_message(self, dest_qq, messageChain):
        data = {
            "sessionKey": self.session_key,
            "target": dest_qq,
            "messageChain": messageChain
        }
        resp = requests.post("{}/sendFriendMessage".format(self.root_url), json=data)
        msg = json.loads(resp.text)["msg"]
        return msg

    def send_group_message(self, messageChain):
        data = {
            "sessionKey": self.session_key,
            "target": self.dest_group_no,
            "messageChain": messageChain
        }
        # print(data)
        resp = requests.post("{}/sendGroupMessage".format(self.root_url), json=data)
        # print(resp.text)
        msg = json.loads(resp.text)["msg"]
        return msg

    def send_group_message_at_list(self, number, stu_list):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今日健康打卡，请以下同学及时完成：".format(no=number)}
        new_line = {"type": "Plain", "text": "\n"}
        # 需要@的QQ列表，组成messageChain
        at_msg_list = []
        for stu in stu_list:
            at_msg_list.append({"type": "At", "target": stu.qq})
            at_msg_list.append(new_line)
        messageChain = [head_text, new_line] + at_msg_list
        return self.send_group_message(messageChain)

    def send_group_message_at_all(self, number):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今日健康打卡，请及时完成。".format(no=number)}
        at_all = {"type": "AtAll"}
        # 需要@的QQ列表，组成messageChain
        messageChain = [head_text, at_all]
        return self.send_group_message(messageChain)

    def send_group_message_text(self, number):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今日健康打卡，请及时完成。".format(no=number)}
        # 需要@的QQ列表，组成messageChain
        messageChain = [head_text]
        return self.send_group_message(messageChain)

    def send_group_message_custom_text(self, text):
        head_text = {"type": "Plain", "text": text}
        # 需要@的QQ列表，组成messageChain
        messageChain = [head_text]
        return self.send_group_message(messageChain)

    def send_group_message_custom_text_custom_at_qq_list(self, text, qq_list):
        head_text = {"type": "Plain", "text": text + "\n"}
        new_line = {"type": "Plain", "text": "\n"}
        # 需要@的QQ列表，组成messageChain
        at_msg_list = []
        for qq in qq_list:
            at_msg_list.append({"type": "At", "target": qq})
            at_msg_list.append(new_line)
        messageChain = [head_text] + at_msg_list
        return self.send_group_message(messageChain)

    def send_group_message_custom_text_custom_at_qq_list_2(self, text, boy_qq_list, girl_qq_list):
        head_text = {"type": "Plain", "text": text}
        new_line = {"type": "Plain", "text": "\n"}
        messageChain = [head_text, new_line]
        # 需要@的QQ列表，组成messageChain
        if boy_qq_list != None and len(boy_qq_list) > 0:
            boy_text = {"type": "Plain", "text": "男生公寓："}
            at_msg_list = []
            for qq in boy_qq_list:
                at_msg_list.append({"type": "At", "target": qq})
                at_msg_list.append(new_line)
            messageChain = messageChain + [boy_text, new_line] + at_msg_list
        if girl_qq_list != None and len(girl_qq_list) > 0:
            girl_text = {"type": "Plain", "text": "女生公寓："}
            at_msg_list = []
            for qq in girl_qq_list:
                at_msg_list.append({"type": "At", "target": qq})
                at_msg_list.append(new_line)
            messageChain = messageChain + [girl_text, new_line] + at_msg_list
        return self.send_group_message(messageChain)


def today_utc_8_date() -> date:
    tz_utc_8 = timezone(timedelta(hours=8))
    utc_8_dt: datetime = datetime.now(timezone.utc).astimezone(tz_utc_8)
    return utc_8_dt.date()


def is_no_check(stu, stu_list):
    '''
    检查某学生是否再一个学生列表内
    :param stu:
    :param stu_list:
    :return:
    '''
    for s in stu_list:
        if stu.id == s.id:
            return True
    return False


def get_no_check_stu_list(wx_username, wx_password):
    # 从完美校园后台获取未提交学生列表，但是信息不全
    wx = WanXiao(wx_username, wx_password)
    wx.login()
    no_check_stu_list = wx.get_no_check_stu_list()
    return no_check_stu_list


def push_to_group(no_check_stu_list, all_stu, qqbot):
    # 再从信息比较全的学生列表中拿出未打卡学生列表
    # 没打卡
    no_check_num = 0
    # 没打卡也没有设置为忽略
    no_check_no_ignore_num = 0
    no_check_stu_list2 = []
    for stu in all_stu:
        # 如果此人确实没有打卡
        if is_no_check(stu, no_check_stu_list):
            # stu_1 = Student(202104241307, "李德银", 2310819457, 0)
            no_check_num += 1  # 因为有人是忽略提醒，所以这里累加的数值可能比需要提醒的要多
            # 不忽略，才加入
            if stu.ignore != True:
                no_check_no_ignore_num += 1
                no_check_stu_list2.append(stu)

    print("当前未打卡的人数{}，当前需要提醒的人数{}".format(no_check_num, no_check_no_ignore_num))

    if no_check_no_ignore_num > 0:
        if no_check_no_ignore_num > 35:
            # 不列出名单，直接at全体成员
            qqbot.send_group_message_at_all(no_check_num)
        elif no_check_no_ignore_num > 20:
            # 不列出名单，也不at，仅文字提醒
            qqbot.send_group_message_text(no_check_num)
        else:
            # 列出名单，at单人
            # 传入包含忽略的未打卡人数，并传入不包含忽略的未打卡列表
            qqbot.send_group_message_at_list(no_check_num, no_check_stu_list2)
    else:
        print("均已健康打卡")


def get_all_stu(conf_path):
    lines = open(conf_path, encoding="utf-8").readlines()
    all_stu = []
    for line in lines[1:]:
        fields = line.strip().split(",")
        all_stu.append(Student(fields[0], fields[1], fields[2], int(fields[3])))
        # print(fields)
    return all_stu


def get_stu_list_of_dormitory_id(dormitory_id: str):
    '''
    根据宿舍号获取宿舍内的人员名单，以姓名列表形式返回
    :param dormitory_id:
    :return:姓名列表
    '''
    lines = open("table/dormitory_stu_table.csv", encoding="utf-8").readlines()
    for line in lines[1:]:
        fields = line.strip().split(",")
        # 如果列表中第1个元素等于传入的宿舍号，则返回姓名列表
        if fields[0] == dormitory_id:
            return fields[1].strip().split("、")


def get_stu_list_of_group_id(group_id: str):
    lines = open("table/group_stu_table.csv", encoding="utf-8").readlines()
    for line in lines[1:]:
        fields = line.strip().split(",")
        # 如果列表中第1个元素等于传入的宿舍号，则返回姓名列表
        if fields[0] == group_id:
            return fields[1].strip().split("、")


def str_to_date(str: str):
    year_s, mon_s, day_s = str.split('-')
    return date(int(year_s), int(mon_s), int(day_s))


def get_boy_dormitory_clean_stu_list_of_date(date: date):
    '''
    获取今日值日生列表
    :return:
    '''
    lines = open("duty_table/boy_dormitory.csv", encoding="utf-8").readlines()
    for line in lines[1:]:
        fields = line.strip().split(",")
        # 获取日期字段，转为date类型
        start_date = str_to_date(fields[0])
        end_date = str_to_date(fields[1])
        # 判断是否在之间
        if start_date <= date <= end_date:
            print("{}介于{}和{}之间".format(date, start_date, end_date))
            dormitory_id = fields[2]
            return get_stu_list_of_dormitory_id(dormitory_id)


def get_girl_dormitory_clean_stu_list_of_date(date: date):
    lines = open("duty_table/girl_dormitory.csv", encoding="utf-8").readlines()
    for line in lines[1:]:
        fields = line.strip().split(",")
        # 获取日期字段，转为date类型
        date1 = str_to_date(fields[0])
        if date1 == date:
            group_id = fields[1]
            return get_stu_list_of_group_id(group_id)


def get_classroom_clean_stu_list_of_date(date: date):
    '''
    获取今日值日生列表
    :return: 学生姓名列表
    '''
    lines = open("duty_table/classroom.csv", encoding="utf-8").readlines()
    for line in lines[1:]:
        fields = line.strip().split(",")
        # 获取日期字段，转为date类型
        start_date = str_to_date(fields[0])
        end_date = str_to_date(fields[1])
        # 判断是否在之间
        if start_date <= date <= end_date:
            print("{}介于{}和{}之间".format(date, start_date, end_date))
            # 如果是多个宿舍，取出宿舍号
            dormitory_ids = fields[2].strip().split("+")
            stu_list_of_dormitory_id = []
            for dormitory_id in dormitory_ids:
                stu_list_of_dormitory_id += get_stu_list_of_dormitory_id(dormitory_id)
            return stu_list_of_dormitory_id


def get_stu_by_name(all_stu, name) -> Student:
    '''
    根据学生（stu）对象列表，返回姓名对应的学生对象
    :param all_stu:
    :param name:
    :return:
    '''
    for stu in all_stu:
        if name == stu.name:
            return stu


def get_stu_list_by_name_list(all_stu, name_list) -> list:
    '''
    根据学生（stu）对象列表与部分同学的姓名，返回姓名列表对应的学生对象列表
    :param all_stu:
    :param name_list:
    :return:
    '''
    stu_list: list = []
    for name in name_list:
        stu_list.append(get_stu_by_name(all_stu, name))
    return stu_list


def get_qq_of_name(all_stu, name):
    '''
    根据学生（stu）对象列表，返回姓名对应的qq号
    :param all_stu:
    :param name:
    :return:
    '''
    for stu in all_stu:
        if name == stu.name:
            return stu.qq


def get_qq_list_of_name_list(all_stu, name_list):
    '''
    根据学生（stu）对象列表，返回姓名列表对应的qq号列表
    :param all_stu:
    :param name_list:
    :return:
    '''
    qq_list = []
    for name in name_list:
        qq_list.append(get_qq_of_name(all_stu, name))
    return qq_list


def get_qq_list_by_stu_list(stu_list: list, check_ignore=False):
    '''
    根据学生对象列表，获取学生QQ列表
    :param stu_list: 学生对象列表
    :param check_ignore: 是否检查忽略情况
    :return:
    '''
    stu_qq_list: list = []
    for stu in stu_list:
        # 如果开启检查忽略情况，和该同学需要忽略，则略过该同学
        if check_ignore and stu.ignore:
            continue
        stu_qq_list.append(stu.qq)
    return stu_qq_list


def push_one_day_three_detection_remind_to_group(conf):
    qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
    qqbot.verify()
    qqbot.bind()
    qqbot.send_group_message_custom_text("关于一日三检表：麻烦大家按时测温并如实填写，双周周末上交。💖🎉")


def push_dormitory_remind_to_group(conf, qqbot, option, add_day: float = 0):
    today = today_utc_8_date()
    if add_day > 0:
        today += timedelta(days=add_day)
    boy_dormitory_today_clean_stu_list = get_boy_dormitory_clean_stu_list_of_date(today)
    girl_dormitory_today_clean_stu_list = get_girl_dormitory_clean_stu_list_of_date(today)
    if (boy_dormitory_today_clean_stu_list is None) and (girl_dormitory_today_clean_stu_list is None):
        print("今日男生女生公寓人员都为无")
        return None

    all_stu = get_all_stu("stu_table.csv")
    if boy_dormitory_today_clean_stu_list != None:
        boy_stu_list = get_stu_list_by_name_list(all_stu, boy_dormitory_today_clean_stu_list)
        boy_qq_list = get_qq_list_by_stu_list(boy_stu_list, check_ignore=True)
    else:
        print("男生值日人员为空")
        boy_qq_list = None
    if girl_dormitory_today_clean_stu_list != None:
        girl_stu_list = get_stu_list_by_name_list(all_stu, girl_dormitory_today_clean_stu_list)
        girl_qq_list = get_qq_list_by_stu_list(girl_stu_list, check_ignore=True)
    else:
        print("女生值日人员为空")
        girl_qq_list = None
    qqbot.send_group_message_custom_text_custom_at_qq_list_2(conf[option]["remind_text"],
                                                             boy_qq_list,
                                                             girl_qq_list)


def push_dormitory_pre_clean_remind_to_group(conf, qqbot):
    '''
    【公寓卫生区预告打扫】提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "dormitory_pre_clean"
    push_dormitory_remind_to_group(conf, qqbot, option, add_day=1)


def push_dormitory_clean_remind_to_group(conf, qqbot):
    '''
    【公寓卫生区打扫】提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "dormitory_clean"
    push_dormitory_remind_to_group(conf, qqbot, option)


def push_dormitory_sign_remind_to_group(conf, qqbot):
    '''
    【公寓卫生区签到】签字提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "dormitory_sign"
    push_dormitory_remind_to_group(conf, qqbot, option)


def push_classroom_remind(conf, qqbot, option):
    '''
    适用于教室打扫的提醒
    :param conf:
    :param qqbot:
    :param option:
    :return:
    '''
    today = today_utc_8_date()
    classroom_today_clean_stu_name_list = get_classroom_clean_stu_list_of_date(today)
    all_stu = get_all_stu("stu_table.csv")
    if classroom_today_clean_stu_name_list != None:
        stu_list = get_stu_list_by_name_list(all_stu, classroom_today_clean_stu_name_list)
        stu_qq_list = get_qq_list_by_stu_list(stu_list, check_ignore=True)
        qqbot.send_group_message_custom_text_custom_at_qq_list(conf[option]["remind_text"], stu_qq_list)
    else:
        print("今天值日人员为空")


def push_after_class_clean_to_group(conf, qqbot):
    '''
    教室下课后提醒打扫 提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "after_class_clean"
    push_classroom_remind(conf, qqbot, option)


def push_after_night_lessons_clean_to_group(conf, qqbot):
    '''
    自习室晚自习后打扫 提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "after_night_lessons_clean"
    push_classroom_remind(conf, qqbot, option)


def push_important_clean_to_group(conf, qqbot):
    '''
    大扫除 提醒
    :param conf:
    :param qqbot:
    :return:
    '''
    option = "important_clean"
    push_classroom_remind(conf, qqbot, option)


def push_remind_text_to_group_by_task_id(conf: dict, task_id: str, qqbot: QQBot):
    tasks = conf["Tasks"]
    for i in tasks:
        if task_id == i["id"]:
            task = Task(i["id"], i["name"], i["remind_text"])
            print("开始提醒任务：{}".format(task.name))
            qqbot.send_group_message_custom_text("【{}】{}".format(task.name, task.remind_text))


def getQQBot(conf):
    qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
    qqbot.verify()
    qqbot.bind()
    return qqbot


def start(health_checkin=False, one_day_three_detection=False
          , dormitory_pre_clean=False
          , dormitory_clean=False
          , dormitory_sign=False
          , after_class_clean=False
          , after_night_lessons_clean=False
          , important_clean=False
          , task_id_list=None
          ):
    print("开发者：青岛黄海学院 2021级计算机科学与技术专升本4班 李德银")
    conf = yaml.load(open("conf.yaml", encoding="utf-8").read(), Loader=yaml.FullLoader)
    qqbot = getQQBot(conf)
    if health_checkin:
        print("开始健康打卡提醒")
        # 将学生表格加载至内存
        all_stu = get_all_stu("stu_table.csv")

        no_check_stu_list = get_no_check_stu_list(conf["wx_account"]["username"], conf["wx_account"]["password"])
        if no_check_stu_list == None or len(no_check_stu_list) == 0:
            print("皆已打卡")
        else:
            push_to_group(no_check_stu_list, all_stu, qqbot)
    if one_day_three_detection:
        print("开始一日三检表提醒")
        push_one_day_three_detection_remind_to_group(conf)
    if dormitory_pre_clean:
        print("开始【公寓卫生区预告打扫】提醒")
        push_dormitory_pre_clean_remind_to_group(conf, qqbot)
    if dormitory_clean:
        print("开始【公寓卫生区打扫】提醒")
        push_dormitory_clean_remind_to_group(conf, qqbot)
    if dormitory_sign:
        print("开始【公寓卫生区打扫后签到】提醒")
        push_dormitory_sign_remind_to_group(conf, qqbot)
    if after_class_clean:
        print("开始【教室下课后提醒打扫】提醒")
        push_after_class_clean_to_group(conf, qqbot)
    if after_night_lessons_clean:
        print("开始【自习室晚自习后打扫】提醒")
        push_after_night_lessons_clean_to_group(conf, qqbot)
    if important_clean:
        print("开始【自习室晚大扫除】提醒")
        push_important_clean_to_group(conf, qqbot)

    if task_id_list is not None:
        print("开始提醒任务列表")
        for task_id in task_id_list:
            push_remind_text_to_group_by_task_id(conf, task_id, qqbot)

    result = qqbot.release()
    print("释放session及其相关资源：{}".format(result))


def SCF_start(event, context):
    # 判断是否含有Message键，如果有就判断并开启某项功能，没有就启用默认选项：提醒健康打卡
    if event.__contains__("Message") and (event["Message"] != None) and (event["Message"] != ""):
        print("接收到Message：" + event["Message"])
        # 相关选项置默认为关闭
        health_checkin = False
        one_day_three_detection = False
        # 宿舍卫生区打扫
        dormitory_clean = False
        # 公寓卫生区预告打扫
        dormitory_pre_clean = False
        # 宿舍卫生区打扫完签字
        dormitory_sign = False
        # 教室下课后提醒打扫
        after_class_clean = False
        # 自习室晚自习后打扫
        after_night_lessons_clean = False
        # 大扫除
        important_clean = False

        # 如果信息里面由包含相关选项，就启动
        if "健康打卡" in event["Message"].split(","):
            print("开始健康打卡提醒")
            health_checkin = True
        if "一日三检表" in event["Message"].split(","):
            print("开始一日三检表提醒")
            one_day_three_detection = True
        if "公寓卫生区预告打扫" in event["Message"].split(","):
            print("开始【公寓卫生区预告打扫】提醒")
            dormitory_pre_clean = True
        if "公寓卫生区打扫" in event["Message"].split(","):
            print("开始【公寓卫生区打扫】提醒")
            dormitory_clean = True
        if "公寓卫生区签到" in event["Message"].split(","):
            print("开始【公寓卫生区签到】提醒")
            dormitory_sign = True
        if "教室下课后打扫" in event["Message"].split(","):
            print("开始【教室下课后打扫】提醒")
            after_class_clean = True
        if "自习室放学后打扫" in event["Message"].split(","):
            print("开始【自习室放学后打扫】提醒")
            after_night_lessons_clean = True
        if "自习室大扫除" in event["Message"].split(","):
            print("开始【自习室大扫除】提醒")
            important_clean = True
        tasks_keyword = "Tasks:"
        task_id_list = None
        if tasks_keyword in event["Message"]:
            argument = event["Message"]
            # 取出子字符串，从tasks_keyword开始，到";"结尾
            tasks_str: str = argument[argument.index(tasks_keyword) + len(tasks_keyword):argument.index(";")]
            task_id_list = tasks_str.split(",")

        start(health_checkin=health_checkin, one_day_three_detection=one_day_three_detection
              , dormitory_pre_clean=dormitory_pre_clean
              , dormitory_clean=dormitory_clean
              , dormitory_sign=dormitory_sign
              , after_class_clean=after_class_clean
              , after_night_lessons_clean=after_night_lessons_clean
              , important_clean=important_clean
              , task_id_list=task_id_list
              )

    else:
        print("未接收到Message，开始运行默认选项")
        start(health_checkin=True)


if __name__ == '__main__':
    args = sys.argv
    # 判断是否输入了别的启动参数，如果有就判断并开启某项功能，没有就启用默认选项：提醒健康打卡
    if len(args) > 1:
        # 相关选项置默认为关闭
        health_checkin = False
        one_day_three_detection = False
        # 宿舍卫生区打扫
        dormitory_clean = False
        # 公寓卫生区预告打扫
        dormitory_pre_clean = False
        # 宿舍卫生区打扫完签字
        dormitory_sign = False
        # 教室下课后提醒打扫
        after_class_clean = False
        # 自习室晚自习后打扫
        after_night_lessons_clean = False
        # 大扫除
        important_clean = False
        if "健康打卡" in args[1:]:
            print("开始健康打卡提醒")
            health_checkin = True
        if "一日三检表" in args[1:]:
            print("开始一日三检表提醒")
            one_day_three_detection = True
        if "公寓卫生区预告打扫" in args[1:]:
            print("开始【公寓卫生区预告打扫】提醒")
            dormitory_pre_clean = True
        if "公寓卫生区打扫" in args[1:]:
            print("开始【公寓卫生区打扫】提醒")
            dormitory_clean = True
        if "公寓卫生区签到" in args[1:]:
            print("开始【公寓卫生区签到】提醒")
            dormitory_sign = True
        if "教室下课后打扫" in args[1:]:
            print("开始【教室下课后打扫】提醒")
            after_class_clean = True
        if "自习室放学后打扫" in args[1:]:
            print("开始【自习室放学后打扫】提醒")
            after_night_lessons_clean = True
        if "自习室大扫除" in args[1:]:
            print("开始【自习室大扫除】提醒")
            important_clean = True
        tasks_keyword = "Tasks:"
        task_id_list = None
        for i in args[1:]:
            if i.startswith(tasks_keyword):
                argument = i
                # 取出子字符串，从tasks_keyword开始，到";"结尾
                tasks_str: str = argument[argument.index(tasks_keyword) + len(tasks_keyword):argument.index(";")]
                task_id_list = tasks_str.split(",")

        start(health_checkin=health_checkin, one_day_three_detection=one_day_three_detection
              , dormitory_pre_clean=dormitory_pre_clean
              , dormitory_clean=dormitory_clean
              , dormitory_sign=dormitory_sign
              , after_class_clean=after_class_clean
              , after_night_lessons_clean=after_night_lessons_clean
              , important_clean=important_clean
              , task_id_list=task_id_list
              )
    else:
        start(health_checkin=True)
