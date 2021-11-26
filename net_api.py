import requests
import json

from beans import Student


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
            "limit": 50,
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
