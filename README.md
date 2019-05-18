# `ex.py`

The `ex.py` utility is a Python 3.6 program that gets arounds the limitations of the web interface of the **FireEye EX** appliance to automate searching email logs more efficiently as well as summarizing results. This is useful during malware or phishing campaigns and is accomplished by carrying out a *linear number* (a unique message identifier set is taken from initial result sets and is subsequently queried for final results) of customized HTTP GET queries that guarantee a complete, scoped search through the identifier of each message. This way all recipients of messages are effectively gathered when distribution lists (*e.g.*, Gmail groups) are used. The utility does not make use of any Application Programming Interface (API), but rather **emulates the behavior of a browser** and keeps plaintext persistent session data (cookies) on the disk to avoid having to re-login.

The utility takes input files for email message **recipients**, **senders** or **sujects** and produces comma-separated value representations of the email traffic logs that match the search parameters. When used together, the utility performs a **linear number of requests** for each subject, recipient and sender. **Unique message identifiers** are then taken and queried for each initial result set, which outputs the final log entries returned by the appliance jobs. This requerying fulfills the scoping needs of accurately sizing campaigns and associated impact because one message identifier can expand to multiple messages not captured beforehand.

The main goal of `ex.py` is to avoid tedious manual searches and to assist cybersecurity analysts. It is thus suitable for incident response and security practitioners alike.

# Dependencies and Usage

The utility requires Python 3.6 and a few modules that are specified in `requirements.txt`. All of them can be installed via `pip3` as follows, optionally upgrading `pip3` first:

```
$ pip3 install --upgrade pip
$ pip3 install -r requirements.txt
```

Problematic installations of `pyjq` and `jq` on macOS can be handled with [`homebrew`](https://brew.sh/) by (re)installing `jq` as follows:

```
$ brew remove jq
$ brew install --HEAD jq
```

One of the main considerations while using the utility is that it performs multiple HTTP requests that create search jobs in the background. For best practice reasons, a moderate use of the search parameters is therefore recommended. The supported options are the following:

```
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
```

# Examples

* Show a help message:

```
$ python3 ex.py -h
```

* Search by recipient address(es) with range "m/d/Y-m/d/Y":

```
$ python3 ex.py -r rcpt.txt "m/d/Y-m/d/Y"
```

* Search by subject(s) and redirect output to a comma-separated value file:

```
$ python3 ex.py --subj subj.txt "m/d/Y-m/d/Y" > data.csv
```

* Search by subject(s) for each sender:

```
$ python3 ex.py -a addr.txt -s subj.txt "m/d/Y-m/d/Y"
```

# Future Work

* Add support for disabling requerying;
* Add support for human-friendly date ranges (*e.g.*, "`now - 3d`") in '`<date>`';
* Possibly integrate alert searches by hash value(s) ('`-h`', '`--hash`'), for instance;
* Python metrics as per https://github.com/rubik/radon.

# Change History

* 20190105: release of v1.0.

# Author

[@dfernan__](https://twitter.com/dfernan__)