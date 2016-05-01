#!/usr/bin/python3

import sys
import os
import subprocess
import argparse
import tempfile
import datetime
import re
import pickle
import hashlib

import build_html
import build_htmlyearplan
import build_latex

diary_pickle_file = os.path.join(os.environ['HOME'], ".cache/diaryas/diary")
org_dir = os.path.join(os.environ['HOME'], "org")
diary_source = ["diary", "anniversaries", "expiry", "leave.el", "roster", "term-dates.el"]
todo_source = ["todo", "pending"]


def get_diary(startdate, enddate):
    """Returns the diary in the form ((DATE, (HOLIDAY, ...), TEXT, TEXT, ...), ..."""
    tf = tempfile.NamedTemporaryFile()
    cp= subprocess.run(["emacs", "--batch", "-Q",
                        "-l",  "~/.emacs-calendar.el",
                        "--eval", "(save-fancy-diary '(%d %d %d) %d \"%s\")" %
                        (startdate.month, startdate.day, startdate.year, (enddate - startdate).days + 1, tf.name)])
    retval = []
    current = None
    reo_date = re.compile(r"((?:Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)[^:]*)[:\s]*([^\Z]+)?")
    reo_underline = re.compile(r"^=+$")
    in_header = False
    for l in tf.readlines():
        l = l.decode().strip()
        mo = reo_date.match(l)
        if mo:
            in_header = True
            retval.append(current)
            current = [mo.group(1), []]
            if mo.group(2):
                current[1].append(mo.group(2))
            continue
        mo = reo_underline.match(l)
        if mo:
            in_header = False
            continue
        if len(l):
            if in_header:
                current[1].append(l)
            else:
                current.append(l)
    retval.append(current)
    del retval[0] #remove None that is appended as first entry
    #replace string date with datetime object
    reo_date = re.compile(r"(\d+)/(\d+)/(\d+)")
    for c, r in enumerate(retval):
        mo = reo_date.search(r[0])
        args = [int(X) for X in reversed(mo.groups())]
        retval[c][0] = datetime.date(*args)
    return retval


def checksum(diary_checksums):
    new_checksums = [ ]
    for fn in diary_source:
        f = open(os.path.join(org_dir, fn), "rb")
        new_checksums.append(hashlib.sha256(f.read()).hexdigest())
    if new_checksums != diary_checksums:
        diary_checksums[:] = new_checksums
        return False
    else:
        return True


if __name__ == "__main__":
    # try:
        parser = argparse.ArgumentParser()
        parser.add_argument("out_format",
                            help="Output format: \t\n"
                            "html | htmlyearplan | latex | text")
        parser.add_argument("-st", "--start-tomorrow", action='store_true',
                            help="Start diary output from tomorrow (html | latex only)")
        parser.add_argument("-c", "--card", action='store_true',
                            help="Create LaTeX sized for 3\" by 5\" index card")
        args = parser.parse_args()
        #load cached variables
        diary_checksums, diary = [ ], [ ]
        if os.path.isfile(diary_pickle_file):
            pf = open(diary_pickle_file, "rb")
            (diary_checksums, diary) = pickle.load(pf)
            pf.close()
        diary_changed = not(checksum(diary_checksums))
        #calculate required dates, use cache if possible
        startdate = datetime.date.today()
        if args.out_format in ("htmlyearplan", "pdfyearplan", "pdfcardyearplan"):
            startdate = startdate.replace(day=1)
            enddate = startdate.replace(year=startdate.year + 1) - datetime.timedelta(days=1)
        else:
            enddate = startdate + datetime.timedelta(days=90)
        if (diary == [ ] or diary_changed or (startdate < diary[0][0]) or (enddate > diary[-1][0])):
            diary = get_diary(startdate, enddate)
        if args.out_format == "html":
            if args.start_tomorrow: startdate += datetime.timedelta(days=1)
            print(build_html.build_html(diary, startdate, enddate))
        elif args.out_format == "htmlyearplan":
            print(build_htmlyearplan.build_html_yearplan(diary, startdate, enddate))
        elif args.out_format == "latex":
            if args.start_tomorrow: startdate += datetime.timedelta(days=1)
            print(build_latex.build_latex(diary, startdate, enddate, args.card))
        else:
            print(args.out_format, " is not supported yet.")
        #store cache
        pf = open(diary_pickle_file, "wb")
        pickle.dump((diary_checksums, diary), pf)
        pf.close()


    # except:
    #     print("Exception")
    #     sys.exit(2)
