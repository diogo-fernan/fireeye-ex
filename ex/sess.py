
import collections, getpass, sys

import bs4, html, requests, urllib, urllib3

import ex.meta, ex.util, ex.web


class Session:
    def __init__(self):
        self.__url = ex.meta.CONFIG.url
        self.__uli = ex.meta.CONFIG.uri_login
        self.__usr = ex.meta.CONFIG.uri_search
        self.__uri = self.__url

        self.sess  = requests.Session()
        if ex.meta.CONFIG.user_agent:
            self.sess.headers["User-Agent"] = ex.meta.CONFIG.user_agent

    @property
    def cookies(self):
        jar = requests.utils.dict_from_cookiejar(self.sess.cookies)
        jar = ex.meta.COOKIES_SEP.join([f"{k}={v}" for k, v in jar.items()])
        return jar

    @cookies.setter
    def cookies(self, jar):
        if jar:
            jar = dict(i.split("=") for i in jar.split(ex.meta.COOKIES_SEP))
            jar = requests.cookies.cookiejar_from_dict(jar)
            self.sess.cookies = jar

    @cookies.deleter
    def cookies(self):
        self.sess.cookies.clear()

    @property
    def uri(self):
        # return urllib.parse.unquote(self.__uri)
        return self.__uri

    @uri.setter
    def uri(self, uri):
        self.__uri = uri

    def default(self):
        self.__uri = self.__url

    def login(self):
        self.__uri = self.__uli

    def search(self, param):
        self.__uri = self.__usr + "?" + urllib3.request.urlencode(param)

    def close(self):
        self.sess.close()

    def __str__(self):
        return str(self.sess) + " " + self.__uri

def session(user=None, cookies=ex.meta.COOKIES_FILE):
    sess = Session()
    if not cookies:
        cookies = ex.meta.COOKIES_FILE
    sess.cookies = ex.util.readf(cookies, ignore=True)
    try:
        while not check(sess):
            del sess.cookies
            if login(sess, user=user):
                break
        ex.util.writef(cookies, sess.cookies)
        return sess
    except requests.exceptions.ConnectionError as e:
        ex.util.error(f"the module 'requests' failed to connect to {sess.uri}.")

def check(sess):
    return ex.web.get(sess)

def login(sess, user=None):
    sess.login()
    res   = ex.web.get(sess)
    soup  = bs4.BeautifulSoup(res.content, "html.parser")
    auth  = soup.find("meta", {"name": "csrf-token"})["content"]

    if not user:
        user = input("username: ")
    passw = getpass.getpass(prompt="password: ", stream=sys.stderr)
    data  = {
        "auth_method": "password",
        "data": {
            "username":  user,
            "password": passw
        }
    }
    headers = {
        # "Content-Type": "application/json",
        # "Referer": sess.uri,
        # "X-Alt-Referrer": sess.uri,
        # "X-CSRF-Param": "authenticity_token",
        "X-CSRF-Token": auth,
        # "X-Requested-With": "XMLHttpRequest"
    }
    sess.sess.headers.update(headers)
    res   = ex.web.post(sess, data, json=True)
    sess.default()
    if res:
        return True
    return False
