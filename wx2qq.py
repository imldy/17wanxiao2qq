from datetime import date, datetime, timezone, timedelta
from beans import Student, Task
from net_api import WanXiao, QQBot
from util import Util
from dao import StudentDao, ClassroomDutyDao, BoyDormitoryDutyDao, GirlDormitoryDutyDao
from factory import BeansFactory
import sys
import yaml


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
        if Util.is_no_check(stu, no_check_stu_list):
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
    today = Util.today_utc_8_date()
    if add_day > 0:
        today += timedelta(days=add_day)
    boy_dormitory_today_clean_stu_list = BoyDormitoryDutyDao.get_boy_dormitory_clean_stu_list_of_date(today)
    girl_dormitory_today_clean_stu_list = GirlDormitoryDutyDao.get_girl_dormitory_clean_stu_list_of_date(today)
    if (boy_dormitory_today_clean_stu_list is None) and (girl_dormitory_today_clean_stu_list is None):
        print("今日男生女生公寓人员都为无")
        return None

    all_stu = StudentDao.get_all_stu("stu_table.csv")
    if boy_dormitory_today_clean_stu_list != None:
        boy_stu_list = StudentDao.get_stu_list_by_name_list(all_stu, boy_dormitory_today_clean_stu_list)
        boy_qq_list = get_qq_list_by_stu_list(boy_stu_list, check_ignore=True)
    else:
        print("男生值日人员为空")
        boy_qq_list = None
    if girl_dormitory_today_clean_stu_list != None:
        girl_stu_list = StudentDao.get_stu_list_by_name_list(all_stu, girl_dormitory_today_clean_stu_list)
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
    today = Util.today_utc_8_date()
    classroom_today_clean_stu_name_list = ClassroomDutyDao.get_classroom_clean_stu_list_of_date(today)
    all_stu = StudentDao.get_all_stu("stu_table.csv")
    if classroom_today_clean_stu_name_list != None:
        stu_list = StudentDao.get_stu_list_by_name_list(all_stu, classroom_today_clean_stu_name_list)
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
    beansFactory = BeansFactory(conf)
    qqbot = beansFactory.getQQBot(conf)
    if health_checkin:
        print("开始健康打卡提醒")
        # 将学生表格加载至内存
        all_stu = StudentDao.get_all_stu("stu_table.csv")

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
