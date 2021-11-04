from datetime import date
from beans import Student
from util import Util


class StudentDao():
    @classmethod
    def get_all_stu(cls, conf_path):
        lines = open(conf_path, encoding="utf-8").readlines()
        all_stu = []
        for line in lines[1:]:
            fields = line.strip().split(",")
            all_stu.append(Student(fields[0], fields[1], fields[2], int(fields[3])))
            # print(fields)
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