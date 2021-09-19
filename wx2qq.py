import requests
import json

import yaml


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
        print(resp.text)
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
            "limit": 50,
            "page": 1,
            "sidx": "",
            "order": "asc",
            # "_": 1631956326256
        }
        resp = self.session.get(url, params=args)
        print(resp.text)
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

    def send_group_message(self, messageChain):
        data = {
            "sessionKey": self.session_key,
            "target": self.dest_group_no,
            "messageChain": messageChain
        }
        print(data)
        resp = requests.post("{}/sendGroupMessage".format(self.root_url), json=data)
        print(resp.text)
        msg = json.loads(resp.text)["msg"]
        return msg

    def send_group_message_at_list(self, number, stu_list):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今天的健康打卡，请以下同学及时完成：".format(no=number)}
        new_line = {"type": "Plain", "text": "\n"}
        # 需要@的QQ列表，组成messageChain
        at_msg_list = []
        for stu in stu_list:
            at_msg_list.append({"type": "At", "target": stu.qq})
            at_msg_list.append(new_line)
        messageChain = [head_text, new_line] + at_msg_list
        return self.send_group_message(messageChain)

    def send_group_message_at_all(self, number):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今天的健康打卡，请及时完成：".format(no=number)}
        at_all = {"type": "AtAll"}
        # 需要@的QQ列表，组成messageChain
        messageChain = [head_text, at_all]
        return self.send_group_message(messageChain)

    def send_group_message_text(self, number):
        head_text = {"type": "Plain", "text": "目前有{no}名同学未完成今天的健康打卡，请及时完成：".format(no=number)}
        # 需要@的QQ列表，组成messageChain
        messageChain = [head_text]
        return self.send_group_message(messageChain)


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


if __name__ == '__main__':
    print("开发者：青岛黄海学院 2021级计算机科学与技术专升本4班 李德银")
    conf = yaml.load(open("conf.yaml").read(), Loader=yaml.FullLoader)
    # 将学生表格加载至内存
    lines = open("stu_table.csv", encoding="utf-8").readlines()
    all_stu = []
    for line in lines[1:]:
        fields = line.strip().split(",")
        all_stu.append(Student(fields[0], fields[1], fields[2], fields[3]))
        # print(fields)

    # 从完美校园后台获取未提交学生列表，但是信息不全
    wx = WanXiao(conf["wx_account"]["username"], conf["wx_account"]["password"])
    wx.login()
    no_check_stu_list = wx.get_no_check_stu_list()

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

    print("当前未打卡的人数{}".format(len(no_check_stu_list2)))
    for i in no_check_stu_list2:
        print("i.id:{},i.name:{},i.qq:{},i.ignore:{}".format(i.id, i.name, i.qq, i.ignore))

    # stu_2 = Student(202104241306, "李德银", 3055325847, 0)
    # no_check_stu_list = [stu_1, stu_2]
    #
    if no_check_no_ignore_num > 0:
        # QQ推送相关
        qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
        qqbot.verify()
        qqbot.bind()
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
