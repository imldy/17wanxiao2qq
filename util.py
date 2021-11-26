from datetime import date, datetime, timezone, timedelta

from mirai import MessageChain, At

from beans import Student, Task, Dest, Crowd, WX_Account, Remind, Bot
from dao import DestDao, CrowdDao
from factory import BeansFactory


class Util():
    @classmethod
    def today_utc_8_date(cls) -> date:
        tz_utc_8 = timezone(timedelta(hours=8))
        utc_8_dt: datetime = datetime.now(timezone.utc).astimezone(tz_utc_8)
        return utc_8_dt.date()

    @classmethod
    def str_to_date(cls, str: str) -> date:
        year_s, mon_s, day_s = str.split('-')
        return date(int(year_s), int(mon_s), int(day_s))

    @classmethod
    def is_no_check(cls, stu: Student, stu_list: list) -> bool:
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

    @classmethod
    def get_qq_list_by_stu_list(cls, stu_list: list, check_ignore=False):
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


class TaskUtil():
    @classmethod
    def parseDict(cls, arg: dict, destDao: DestDao, crowdDao: CrowdDao) -> Task:
        task = Task(arg["id"], arg["name"], arg["remind_text"])
        # 处理消息目的地
        if "dest" in arg:
            dest: Dest = destDao.getDestByTag(arg["dest"])
            task.dest = dest
        if "remind_text_private_chat" in arg:
            task.remind_text_private_chat = arg["remind_text_private_chat"]
        # 处理涉及人群
        if "involve_crowd" in arg:
            crow = crowdDao.getCrowdByTag(arg["involve_crowd"])
            task.involve_crowd = crow

        # 处理提醒类型
        if "remind_type" in arg:
            if arg["remind_type"].lower() == Remind.PLAIN.lower():
                task.remind_type = Remind.PLAIN
            if arg["remind_type"].lower() == Remind.NEED_AT.lower():
                task.remind_type = Remind.NEED_AT
        if "date" in arg:
            if arg["date"] == "today":
                # task.date = Util.today_utc_8_date() # 如果需要获取今日值
                task.date = arg["date"]
            # 以后可增加处理其他基准时间
        else:
            # 默认当天
            task.date = "today"
        if "date_offset" in arg:
            try:
                task.date_offset = int(arg["date_offset"])
            except Exception as e:
                print(e)
                task.date_offset = 0
        else:
            task.date_offset = 0

        return task


class CrowdUtil():
    @classmethod
    def parseDict(cls, arg: dict):
        crowd = Crowd()
        # 处理固定的标签
        if arg["tag"].lower() == Crowd.CLASS_ALL.lower():
            crowd.tag = Crowd.CLASS_ALL
        elif arg["tag"].lower() == Crowd.WX_NO_HEALTH_CHECKIN.lower():
            crowd.tag = Crowd.WX_NO_HEALTH_CHECKIN
            crowd.account = WX_Account(arg["wx_account"]["username"], arg["wx_account"]["password"])
        elif arg["tag"].lower() == Crowd.BOY_DORMITORY_CLEANER.lower():
            crowd.tag = Crowd.BOY_DORMITORY_CLEANER
        elif arg["tag"].lower() == Crowd.GIRL_DORMITORY_CLEANER.lower():
            crowd.tag = Crowd.GIRL_DORMITORY_CLEANER
        elif arg["tag"].lower() == Crowd.CLASSROOM_CLEANER.lower():
            crowd.tag = Crowd.CLASSROOM_CLEANER
        else:
            # 非固定标签
            pass
        # 处理姓名
        if "name" in arg:
            crowd.name = arg["name"]
        return crowd


class DestUtil():
    @classmethod
    def parseDict(cls, arg: dict):
        dest = Dest(arg["tag"])
        if arg["type"].lower() == Dest.GROUP.lower():
            dest.type = Dest.GROUP
        elif arg["type"].lower() == Dest.PERSON.lower():
            dest.type = Dest.PERSON
        elif arg["type"].lower() == Dest.PRIVATE_CHAT.lower():
            dest.type = Dest.PRIVATE_CHAT
        if "no" in arg:
            dest.no = arg["no"]
        if "nos" in arg:
            dest.nos = arg["nos"]
        if "email" in arg:
            dest.email = arg["email"]
        return dest


class BotUtil():
    @classmethod
    def parseDict(cls, arg: dict) -> Bot:
        bot = Bot(arg["tag"])
        if arg["type"].lower() == Bot.MIRAI_API_HTTP_HTTP:
            bot.type = Bot.MIRAI_API_HTTP_HTTP
        if "qq_no" in arg:
            bot.qq_no = ["qq_no"]
        if "root_url" in arg:
            bot.root_url = ["root_url"]
        if "verify_key" in arg:
            bot.verify_key = ["verify_key"]
        return bot


class StudentUtil():
    @classmethod
    def getStuNoListByStuList(cls, stuList: list) -> list:
        '''
        根据学生对象列表，获取学生学号列表
        :return:
        '''
        stuNoList = []
        for stu in stuList:
            stuNoList.append(stu.id)
        return stuNoList
