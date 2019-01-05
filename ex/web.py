
import collections, getpass
import bs4, html, urllib3

import ex.meta, ex.util


class InvalidSession(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def get(sess, json=False):
    res = sess.sess.get(
        sess.uri,
        allow_redirects=False,
        # proxies=<proxy>,
        timeout=ex.meta.CONFIG.timeout,
        verify=False
    )
    if res.headers.get("Location") == ex.meta.CONFIG.uri_logout:
        return None
    elif res.status_code == 302 or res.status_code == 203:
        # raise InvalidSession(f"received response code {res.status_code}")
        return None
    if json:
        try:
            res = res.json()
            if "location" in res:
                return None
                # raise InvalidSession("invalid session")
            return res
        except ValueError:
            return {}
    # elif res.text:
    #    return res
    return res

def post(sess, data, json=False):
    if not json:
        data = urllib3.request.urlencode(data)
    res  = sess.sess.post(
        sess.uri,
        allow_redirects=False,
        # data=data,
        json=data,
        timeout=ex.meta.CONFIG.timeout,
        verify=False
    )
    if res.headers.get("Location") == ex.meta.CONFIG.url:
        return res
    # elif res.status_code == 302 or res.status_code == 203:
    #    return None
    elif res.headers.get("Location") == ex.meta.CONFIG.uri_login:
        return None
    else:
        return None
