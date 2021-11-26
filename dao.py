from datetime import date
from beans import Student, Task, Dest, Bot
from factory import BeansFactory
from util import Util, TaskUtil, CrowdUtil, DestUtil, BotUtil


class StudentDao():
    all_stu = None
    conf_path = None

    @classmethod
    def get_all_stu(cls, conf_path):
        lines = open(conf_path, encoding="utf-8").readlines()
        all_stu = []
        for line in lines[1:]:
            fields = line.strip().split(",")
            all_stu.append(Student(fields[0], fields[1], fields[2], int(fields[3])))
            # print(fields)
        cls.all_stu = all_stu
        cls.conf_path = conf_path
        return all_stu

    @classmethod
    def get_stu_list_of_dormitory_id(cls, dormitory_id: str):
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

    @classmethod
    def get_stu_list_of_group_id(cls, group_id: str):
        lines = open("table/group_stu_table.csv", encoding="utf-8").readlines()
        for line in lines[1:]:
            fields = line.strip().split(",")
            # 如果列表中第1个元素等于传入的宿舍号，则返回姓名列表
            if fields[0] == group_id:
                return fields[1].strip().split("、")

    @classmethod
    def get_stu_by_name(cls, all_stu, name) -> Student:
        '''
        根据学生（stu）对象列表，返回姓名对应的学生对象
        :param all_stu:
        :param name:
        :return:
        '''
        for stu in all_stu:
            if name == stu.name:
                return stu

    @classmethod
    def get_stu_list_by_name_list(cls, all_stu, name_list) -> list:
        '''
        根据学生（stu）对象列表与部分同学的姓名，返回姓名列表对应的学生对象列表
        :param all_stu:
        :param name_list:
        :return:
        '''
        stu_list: list = []
        for name in name_list:
            stu_list.append(StudentDao.get_stu_by_name(all_stu, name))
        return stu_list

    @classmethod
    def get_qq_of_name(cls, all_stu, name):
        '''
        根据学生（stu）对象列表，返回姓名对应的qq号
        :param all_stu:
        :param name:
        :return:
        '''
        for stu in all_stu:
            if name == stu.name:
                return stu.qq

    @classmethod
    def get_qq_list_of_name_list(cls, all_stu, name_list):
        '''
        根据学生（stu）对象列表，返回姓名列表对应的qq号列表
        :param all_stu:
        :param name_list:
        :return:
        '''
        qq_list = []
        for name in name_list:
            qq_list.append(StudentDao.get_qq_of_name(all_stu, name))
        return qq_list

    @classmethod
    def getStuListByStuNoList(cls, stuNoList: list, enbaleIgnore=True) -> list:
        '''
        根据学号列表，获取学号列表对应的学生列表
        :param stuNoList: 学号列表
        :param enbaleIgnore: 启用判断是否忽略学生
        :return:
        '''
        if cls.all_stu == None:
            cls.get_all_stu(cls.conf_path)
        stuList: list = []
        for stu in cls.all_stu:
            # 如果在某个列表中
            if stu.id in stuNoList:
                if stu.ignore and enbaleIgnore:
                    # 如果 要忽略 并且 启用忽略判断
                    continue
                stuList.append(stu)
        return stuList


class ClassroomDutyDao():
    @classmethod
    def get_classroom_clean_stu_list_of_date(cls, date: date):
        '''
        获取今日值日生列表
        :return: 学生姓名列表
        '''
        lines = open("duty_table/classroom.csv", encoding="utf-8").readlines()
        for line in lines[1:]:
            fields = line.strip().split(",")
            # 获取日期字段，转为date类型
            start_date = Util.str_to_date(fields[0])
            end_date = Util.str_to_date(fields[1])
            # 判断是否在之间
            if start_date <= date <= end_date:
                print("{}介于{}和{}之间".format(date, start_date, end_date))
                # 如果是多个宿舍，取出宿舍号
                dormitory_ids = fields[2].strip().split("+")
                stu_list_of_dormitory_id = []
                for dormitory_id in dormitory_ids:
                    stu_list_of_dormitory_id += StudentDao.get_stu_list_of_dormitory_id(dormitory_id)
                return stu_list_of_dormitory_id


class GirlDormitoryDutyDao():
    @classmethod
    def get_girl_dormitory_clean_stu_list_of_date(cls, date: date):
        lines = open("duty_table/girl_dormitory.csv", encoding="utf-8").readlines()
        for line in lines[1:]:
            fields = line.strip().split(",")
            # 获取日期字段，转为date类型
            date1 = Util.str_to_date(fields[0])
            if date1 == date:
                group_id = fields[1]
                return StudentDao.get_stu_list_of_group_id(group_id)


class BoyDormitoryDutyDao():
    @classmethod
    def get_boy_dormitory_clean_stu_list_of_date(cls, date: date):
        '''
        获取今日值日生列表
        :return:
        '''
        lines = open("duty_table/boy_dormitory.csv", encoding="utf-8").readlines()
        for line in lines[1:]:
            fields = line.strip().split(",")
            # 获取日期字段，转为date类型
            start_date = Util.str_to_date(fields[0])
            end_date = Util.str_to_date(fields[1])
            # 判断是否在之间
            if start_date <= date <= end_date:
                print("{}介于{}和{}之间".format(date, start_date, end_date))
                dormitory_id = fields[2]
                return StudentDao.get_stu_list_of_dormitory_id(dormitory_id)


class TaskDao():
    def __init__(self, conf: dict):
        self.conf: dict = conf
        self.taskList = None
        self.beansFactory = BeansFactory(conf)
        self.destDao = self.beansFactory.getDestDao()

    def getAllTask(self) -> list:
        taskList = []
        for i in self.conf["Tasks"]:
            task: Task = TaskUtil.parseDict(i, self.destDao)
            taskList.append(task)
        self.taskList = taskList
        return taskList

    def getTaskById(self, id: str) -> Task:
        if self.taskList == None:
            self.taskList = self.getAllTask()
        for task in self.taskList:
            if id == task.id:
                return task


class CrowdDao():
    def __init__(self, conf: dict):
        self.conf: dict = conf
        self.crowdList = None

    def getAllCrowd(self) -> list:
        crowdList = []
        for i in self.conf["Crowds"]:
            crowd = CrowdUtil.parseDict(i)
            crowdList.append(crowd)
        self.crowdList = crowdList
        return crowdList

    def getCrowdByTag(self, tag: str):
        if self.crowdList == None:
            self.crowdList = self.getAllCrowd()
        for corwd in self.crowdList:
            if tag == corwd.tag:
                return corwd


class DestDao():
    def __init__(self, conf: dict):
        self.conf: dict = conf
        self.destList = None

    def getAllDest(self) -> list:
        destList = []
        for i in self.conf["Destinations"]:
            dest = DestUtil.parseDict(i)
            destList.append(dest)
        return destList

    def getDestByTag(self, tag: str) -> Dest:
        if self.destList == None:
            self.destList = self.getAllDest()
        for dest in self.destList:
            if tag == dest.tag:
                return dest


class BotDao():
    def __init__(self, conf: dict):
        self.conf: dict = conf
        self.botList = None

    def getAllBot(self) -> list:
        botList = []
        for i in self.conf["Bots"]:
            bot = BotUtil.parseDict(i)
            botList.append(bot)
        return botList

    def getBotByTag(self, tag: str) -> Bot:
        if self.botList == None:
            self.botList = self.getAllBot()
        for bot in self.botList:
            if tag == bot.tag:
                return bot


if __name__ == '__main__':
    print(Dest.GROUP)
