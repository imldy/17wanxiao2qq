class Task():
    def __init__(self, id, name, remind_text):
        self.id = id  # 任务ID
        self.name = name  # 任务名
        self.remind_text = remind_text  # 任务提醒语句，描述语句
        self.remind_type = None  # 提醒类型，简单的文本|需要at的
        self.dest = None  # 任务目的地，某个群或者某个QQ账号
        self.involve_crowd = None  # 消息中涉及到的人
        self.date = None  # 标准日期
        self.date_offset = None  # 标准日期的偏移量，+1代表提前一天


class Student():
    def __init__(self, id, name, qq, ignore):
        self.id = id
        self.name = name
        self.qq = qq
        if ignore == 0:
            self.ignore = False
        else:
            self.ignore = True


class Dest():
    GROUP = "GROUP"
    PERSON = "PERSON"
    PRIVATE_CHAT = "PRIVATE_CHAT"

    def __init__(self, tag: str):
        self.tag: str = tag
        self.type: str = None
        self.no: str = None
        self.nos: str = None
        self.email: str = None


class Crowd():
    CLASS_ALL = "class-all"
    WX_NO_HEALTH_CHECKIN = "wx-no-health-checkin"
    BOY_DORMITORY_CLEANER = "boy-dormitory-cleaner"
    GIRL_DORMITORY_CLEANER = "girl-dormitory-cleaner"
    CLASSROOM_CLEANER = "classroom-cleaner"

    def __init__(self):
        self.tag: str = None
        self.name: str = None


class Account():
    def __init__(self, username, password):
        self.username = username
        self.password = password


class WX_Account(Account):
    pass


class Remind():
    PLAIN = "plain"
    NEED_AT = "Need At"


class Bot():
    MIRAI_API_HTTP_HTTP = "mirai-api-http http"
    MIRAI_API_HTTP_ws = "mirai-api-http ws"

    def __init__(self, tag):
        self.tag = tag
        self.type = None
        self.qq_no = None
        self.root_url = None
        self.verify_key = None
