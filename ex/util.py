
import json, pprint, re, sys

from ex.meta import DATE_FRMT, DATE_SEP


def error(msg, kie=True):
    print(f"\n ERROR: {msg}", file=sys.stderr)
    # sys.exit(1)
    if kie:
        raise KeyboardInterrupt

def date(str):
    if str:
        from datetime import datetime
        try:
            start, end = str.split(DATE_SEP)
            start, end = start.strip(), end.strip()
            start = datetime.strptime(start, DATE_FRMT).strftime(DATE_FRMT)
            end   = datetime.strptime(end,   DATE_FRMT).strftime(DATE_FRMT)
            if start > end:
                raise Exception
            return (start, end)
        except:
            error("invalid date range")
    # return datedefault()
    return None

def datedefault(days=5):
    from datetime import datetime, timedelta
    dt    = datetime.today()
    start = (dt - timedelta(days=days)).strftime(DATE_FRMT)
    end   = dt.strftime(DATE_FRMT)
    return (start, end)

def readf(file, mode='r', lines=False, dice=False, ignore=False, read=True):
    try:
        fd = open(file, encoding="utf-8", mode=mode)
        if not read:
            fd.close()
            return True
        data = fd.read()
        fd.close()
        # if not data:
        #    error(f"file \"{file}\" is empty", execpt=False)
        data = data.rstrip()  # "\r\n"
        if lines:
            data = data.splitlines()
        elif dice:
            data = re.split(r"\s+|,|;", data)
        else:
            return data
        return list(filter(None, data))
    except:
        if ignore:
            return False
        error(f"cannot open file \"{file}\"")

def writef(file, data, mode='w'):
    try:
        fd = open(file, encoding="utf-8", mode=mode)
        fd.write(data)
        fd.close()
    except:
        error(f"cannot write file \"{file}\"")

def jsond(data):
    return json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True)

def jsonp(data):
    # pprint.pprint(jsond(data))
    print(jsond(data))
