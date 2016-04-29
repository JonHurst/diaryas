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

pickle_file = os.path.join(os.environ['HOME'], ".cache/diaryas/cache")
org_dir = os.path.join(os.environ['HOME'], "org")
diary_source = ["diary", "anniversaries", "expiry", "leave.el", "roster", "term-dates.el"]
todo_source = ["todo", "pending"]


def get_diary(days, startdate):
    """Returns the diary in the form ((DAY_DESCRIPTOR, (HOLIDAY, ...), TEXT, TEXT, ...), ..."""
    tf = tempfile.NamedTemporaryFile()
    print("Running")
    cp= subprocess.run(["emacs", "--batch", "-Q",
                        "-l",  "~/.emacs-calendar.el",
                        "--eval", "(save-fancy-diary '(%d %d %d) %d \"%s\")" %
                        (startdate.month, startdate.day, startdate.year, days, tf.name)])
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
    return retval[1:]


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
                            "html | htmlyearplan | text | pdf | pdfcards | pdfyearplan | pdfcardyearplan")
        args = parser.parse_args()
        #load cached variables
        diary_checksums, diary = [ ], [ ]
        if os.path.isfile(pickle_file):
            pf = open(pickle_file, "rb")
            (diary_checksums, diary) = pickle.load(pf)
            pf.close()
        diary_changed = not(checksum(diary_checksums))
        if diary_changed:
            #startdate startdate is first day of current month
            startdate = datetime.date.today().replace(day=1)
            days = (startdate.replace(year=startdate.year + 1) - startdate).days + 1
            #retrieve the data
            diary = get_diary(days, startdate)
        print(diary)
        #store cache
        pf = open(pickle_file, "wb")
        pickle.dump((diary_checksums, diary), pf)
        pf.close()


    # except:
    #     print("Exception")
    #     sys.exit(2)
