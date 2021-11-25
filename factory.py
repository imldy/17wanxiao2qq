from dao import TaskDao, DestDao, BotDao
from net_api import QQBot
from wx2qq import WX2QQService


class BeansFactory():
    def __init__(self, conf):
        self.conf = conf

    def getBeans(self, beans_name: str):
        if beans_name.lower() == "QQBot".lower():
            return self.getQQBot(self.conf)
        elif beans_name.lower() == "WX2QQService".lower():
            return self.getWX2QQService(self.conf)

    def getQQBot(self, conf=None):
        if conf == None:
            conf = self.conf
        qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
        qqbot.verify()
        qqbot.bind()
        return qqbot

    def getWX2QQService(self, conf=None):
        wx2QQService = WX2QQService(conf)
        return wx2QQService

    def getTaskDao(self, conf=None):
        taskDao = TaskDao(conf)
        return taskDao

    def getDestDao(self, conf=None):
        destDao = DestDao(conf)
        return destDao

    def getBotDao(self, conf=None) -> BotDao:
        botDao = BotDao(conf)
        return botDao
