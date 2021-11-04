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