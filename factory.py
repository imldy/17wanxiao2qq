from net_api import QQBot


class BeansFactory():
    def __init__(self, conf):
        self.conf = conf

    def getBeans(self, beans_name: str):
        if beans_name.lower() == "QQBot".lower():
            return self.getQQBot(self.conf)

    def getQQBot(self, conf=None):
        if conf == None:
            conf = self.conf
        qqbot = QQBot(conf["root_url"], conf["verify_key"], conf["dest_group"], conf["bot_qq"])
        qqbot.verify()
        qqbot.bind()
        return qqbot
