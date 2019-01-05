#!/usr/bin/env python3

"""
Usage: ex [-h] [-u <user> | -c <jar>]
          ([-a <addr> -r <rcpt> -s <subj>])
          [<date>]

Query FireEye EX email appliances for email traffic logs and output email
traffic logs in comma-separated value format. Developed and tested on appliance
model CM9400 with version 8.3.

Configurations are specified in the "./config.yml" file while plaintext
persistent session data (cookies) are saved in "./cookies.txt". Both of these
are automatically read from the current working directory, having the
possibility of specifying another cookie jar file with the '-c' option. Note
that TLS/SSL warnings (e.g, expired certificates) are disabled through the
"urllib3" module facility for that purpose.

Options:
  -h, --help         show this help message and exit
  -c, --cook <jar>   file with cookie jar (useful when copying cookies from browsers)
  -u, --user <user>  login username

Search fields (use '%' as wildcard):
  -a, --addr <addr>  file with sender address(es) to search for
  -r, --rcpt <rcpt>  file with recipient address(es) to search for
  -s, --subj <subj>  file with subject(s) to search for (case sensitive)
  <date>  date range with format "%m/%d/%Y-%m/%d/%Y" (appliance default applies if not specified)

Requirements:
  - Python 3.6;
  - Dependencies are specified in "requirements.txt" and can be installed via
    "pip3" as follows, optionally upgrading "pip3" first:
$ pip3 install --upgrade pip
$ pip3 install -r requirements.txt
  - Problematic installations of "pyjq" with "jq" on macOS can be handled by
    "homebrew" by (re)installing "jq" as follows:
$ brew remove jq
$ brew install --HEAD jq

Examples:
  - Show a help message:
$ python3 ex.py -h
  - Search by recipient address(es) with range "m/d/Y-m/d/Y":
$ python3 ex.py -r rcpt.txt "m/d/Y-m/d/Y"
  - Search by subject(s) and redirect output to a comma-separated value file:
$ python3 ex.py --subj subj.txt "m/d/Y-m/d/Y" > data.csv
  - Search by subject(s) for each sender:
$ python3 ex.py -a addr.txt -s subj.txt "m/d/Y-m/d/Y"

Future work:
  - Add support for disabling requerying;
  - Add support for human-friendly date ranges (e.g., "now - 3d") in "<date>";
  - Possibly integrate alert searches by hash value(s) ('-h', '--hash'), for
    instance;
  - Python metrics as per https://github.com/rubik/radon.

Copyright (c) 2019 Diogo Fernandes
https://github.com/diogo-fernan
"""


import collections, os, re, sys
import docopt, pyjq, requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

import ex.meta, ex.sess, ex.srch, ex.util


def cleanup(signum, frame):
    # import signal
    # signal.signal(signal.SIGINT, cleanup)
    sys.exit(0)

if __name__ == "__main__":
    arg = docopt.docopt(__doc__)
    ex.meta.init()

    # "http_proxy" missing
    https_proxy = ""
    if "https_proxy" in os.environ:
        https_proxy = os.environ["https_proxy"]
        del os.environ["https_proxy"]

    session = None
    try:
        date = ex.util.date(arg["<date>"])

        addr, rcpt, subj = None, None, None
        if arg["--addr"]:
            addr = ex.util.readf(arg["--addr"], dice=True)
        if arg["--rcpt"]:
            rcpt = ex.util.readf(arg["--rcpt"], dice=True)
        if arg["--subj"]:
            subj = ex.util.readf(arg["--subj"], dice=True)

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        session = ex.sess.session(user=arg["--user"], cookies=arg["--cook"])

        ex.srch.search(session, date, addr, rcpt, subj)

    except KeyboardInterrupt:
        if https_proxy:
            os.environ["https_proxy"] = https_proxy
        if session:
            session.close()
        sys.exit(1)
