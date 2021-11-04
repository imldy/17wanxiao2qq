from datetime import date, datetime, timezone, timedelta
from beans import Student


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
