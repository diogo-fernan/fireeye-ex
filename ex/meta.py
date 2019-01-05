
CONFIG_FILE  = "./config.yml"
COOKIES_FILE = "./cookies.txt"
COOKIES_SEP  = "; "

DATE_FRMT    = "%m/%d/%Y"
DATE_SEP     = "-"
WILDCARD     = "%"


class Config:
    param = [
        "hostname",
        "name",
        "proto",
        "search_sleep",
        "timeout",
        "user_agent"
    ]

    def __init__(self):
        self.__hostname      = ""
        self.__name          = "fireeye-ex"
        self.__proto         = "https"
        self.__search_sleep  = 3
        self.__timeout       = 120
        self.__uri_alert     = ""
        self.__uri_login     = ""
        self.__uri_logout    = ""
        self.__uri_search    = ""
        self.__url           = ""
        self.__user_agent    = "fireeye-ex ex.py"

    @property
    def hostname(self):
        return self.__hostname

    @hostname.setter
    def hostname(self, hostname):
        self.__hostname = hostname
        self.url = hostname

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def search_sleep(self):
        return self.__search_sleep

    @search_sleep.setter
    def search_sleep(self, search_sleep):
        if type(search_sleep) != int:
            raise TypeError
        self.__search_sleep = search_sleep

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout):
        if type(timeout) != int:
            raise TypeError
        self.__timeout = timeout

    @property
    def uri_login(self):
        return self.__uri_login

    @property
    def uri_logout(self):
        return self.__uri_logout

    @property
    def uri_search(self):
        return self.__uri_search

    @property
    def uri_alert(self):
        return self.__uri_alert

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, hostname):
        self.__url        = self.__proto + "://" + hostname + "/"
        self.__uri_login  = self.__url + "login/login"
        self.__uri_logout = self.__url + "login/logout"
        self.__uri_search = self.__url + "cms/message_tracking/messages"
        self.__uri_alert  = self.__url + ""  # not implemented yet

    @property
    def user_agent(self):
        return self.__user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self.__user_agent = user_agent

CONFIG = Config()

def init():
    import yaml
    import ex.util
    if ex.util.readf(CONFIG_FILE, read=False):
        try:
            cfg = yaml.safe_load(open(CONFIG_FILE))
        except yaml.scanner.ScannerError:
            ex.util.error(f"\"{CONFIG_FILE}\" is not a proper YAML file",
                kie=False)
        key = [i for i in Config.param if i not in cfg]
        if len(key) == 0:
            try:
                for k, v in cfg.items():
                    setattr(CONFIG, k, v)
            except TypeError:
                ex.util.error(f"parameter \"{k}\" from \"{CONFIG_FILE}\" is not valid",
                    kie=False)
        else:
            ex.util.error(f"parameter(s) \"{key}\" is(are) missing from \"{CONFIG_FILE}\"",
                kie=False)
