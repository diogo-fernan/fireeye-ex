
import collections, csv, getpass, os, re, signal, sys, time

import bs4, html, pyjq, requests

import ex.meta, ex.util, ex.web


class Search():
    def __init__(self):
        # super().__init__(self)
        self.param = collections.OrderedDict([
            ("appliances", "All"),
            ("group_filter", "All"),
            # ("job_id", 0),
            ("num", 999),
            # ("offset", 0),
            ("search[chosenLabel]", "Custom"),
            # ("search[end_date]", ""),
            # ("search[message_tracker_id]", ""),
            # ("search[recipient]", ""),
            # ("search[sender]", ""),
            # ("search[start_date]", ""),
            # ("search[subject_line]", ""),
            ("sort", ""),
            ("sort_by", "")
        ])

    @property
    def date(self):
        return (self.__get("search[start_date]"), self.__get("search[end_date]"))

    @date.setter
    def date(self, daterange):
        if daterange and type(daterange) == tuple:
            self.param["search[start_date]"] = daterange[0]
            self.param["search[end_date]"]   = daterange[1]
        elif not daterange:
            self.__del("search[chosenLabel]")

    @date.deleter
    def date(self):
        self.__del("search[start_date]")
        self.__del("search[end_date]")

    @property
    def addr(self):
        return self.__get("search[sender]")

    @addr.setter
    def addr(self, addr):
        del self.mid, self.jid
        self.param["search[sender]"] = addr

    @addr.deleter
    def addr(self):
        self.__del("search[sender]")

    @property
    def rcpt(self):
        return self.__get("search[recipient]")

    @rcpt.setter
    def rcpt(self, rcpt):
        del self.mid, self.jid
        self.param["search[recipient]"] = rcpt

    @rcpt.deleter
    def rcpt(self):
        self.__del("search[recipient]")

    @property
    def subj(self):
        return self.__get("search[subject_line]")

    @subj.setter
    def subj(self, subj):
        del self.mid, self.jid
        self.param["search[subject_line]"] = subj

    @subj.deleter
    def subj(self):
        self.__del("search[subject_line]")

    @property
    def jid(self):
        return self.__get("job_id")

    @jid.setter
    def jid(self, jid):
        del self.addr, self.rcpt, self.subj, self.mid
        self.param["job_id"] = jid

    @jid.deleter
    def jid(self):
        self.__del("job_id")

    @property
    def mid(self, mid):
        return self.__get("search[message_tracker_id]")

    @mid.setter
    def mid(self, mid):
        del self.addr, self.rcpt, self.subj, self.jid
        self.param["search[message_tracker_id]"] = mid

    @mid.deleter
    def mid(self):
        self.__del("search[message_tracker_id]")

    def __get(self, param):
        return self.param.get(param)

    def __del(self, param):
        self.param.pop(param, None)

    def __str__(self):
        return str(self.param)

def job(session, search):
    session.search(search.param)
    res = ex.web.get(session, json=True)
    search.jid = res["job_id"]
    session.search(search.param)
    while True:
        res = ex.web.get(session, json=True)
        if res["job_status"] != "completed":  # and res["list"]:
            # log res["job_status"]
            time.sleep(ex.meta.CONFIG.search_sleep)
        else:
            # print(res)
            break
    return res

def search(session, daterange, addr, rcpt, subj):
    search = Search()
    search.date = daterange

    if not addr:
        addr = [ex.meta.WILDCARD]
    if not rcpt:
        rcpt = [ex.meta.WILDCARD]
    if not subj:
        subj = [ex.meta.WILDCARD]

    data = []
    for i in addr:
        for j in rcpt:
            for k in subj:
                search.addr, search.rcpt, search.subj = i, j, k
                res = job(session, search)
                if res:
                    mid = pyjq.all(".list | .[] | .message_id", res)
                    for l in mid:
                        search.mid = l
                        res = job(session, search)
                        if res:
                            res = pyjq.all(".list[]", res)
                            data += [m for m in res if m not in data]
                            # for l in res:
                            #    if l not in data:
                            #        data += [l]

    if data:
        data = pyjq.all(
                '.[].url_list |= map(['
                ' .url,'
                ' (if .malicious == false then "not malicious" else "malicious" end),'
                ' (if has(".not_scanned_reason") then .not_scanned_reason else "not scanned" end)'
                ']) | .[]', data)
        data = pyjq.all(
                '.[].attachment_list |= map(['
                ' .attachment,'
                ' (if .malicious == false then "not malicious" else "malicious" end),'
                ' (if has(".not_scanned_reason") then .not_scanned_reason else "not scanned" end)'
                ']) | .[]', data)

        keys  = data[0].keys()
        # "date" format: "mm/dd/yy HH:MM:SS"
        data  = sorted(data, key=lambda row: row["date"])
        dataf = csv.DictWriter(sys.stdout, keys)
        dataf.writeheader()
        dataf.writerows(data)


    # for l in res:
    #    if l not in data:
    #        l["url_list"] = [list(i.items()) for i in l["url_list"]]
    #        data += [l]

    # https://stackoverflow.com/questions/53250318/jq-update-list-elements-based-on-values

