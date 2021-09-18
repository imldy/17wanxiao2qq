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
        self.session.post("http://reported.17wanxiao.com/login.html")
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
            "nd": 1631956327043,  # 截至时间
            "limit": 50,
            "page": 1,
            "sidx": "",
            "order": "asc",
            "_": 1631956326256
        }
        resp = self.session.get(url, params=args)
        print(resp.text)
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

    def send_group_message(self, stu_list):
        head_text = {"type": "Plain", "text": "请以下同学及时健康打卡："}
        new_line = {"type": "Plain", "text": "\n"}
        # 需要@的QQ列表，组成messageChain
        at_msg_list = []
        for stu in stu_list:
            at_msg_list.append({"type": "At", "target": stu.qq})
            at_msg_list.append(new_line)
        messageChain = [head_text, new_line] + at_msg_list
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


if __name__ == '__main__':
    print("开发者：青岛黄海学院 2021级计算机科学与技术专升本4班 李德银")
    conf = yaml.load(open("conf.yaml").read(), Loader=yaml.FullLoader)
    wx = WanXiao(conf["wx_account"]["username"], conf["wx_account"]["password"])
    wx.login()
    wx.get_no_check_stu_list()
    # stu_1 = Student(202104241307, "李德银", 2310819457, 0)
    # stu_2 = Student(202104241306, "李德银", 3055325847, 0)
    # no_check_stu_list = [stu_1, stu_2]
    #
    # # QQ推送相关
    # qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
    # qqbot.verify()
    # qqbot.bind()
    # qqbot.send_group_message(no_check_stu_list)
