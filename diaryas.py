#!/usr/bin/python3

import os
import subprocess
import argparse
import tempfile
import datetime
import re

import build_html
import build_htmlyearplan
import build_latex
import build_latexyearplan


def get_diary(startdate, enddate):
    """
    Returns the diary in the form
     ((DATE, (HOLIDAY, ...), (TAG, ...), TEXT, TEXT, ...), ...
    """
    tf = tempfile.NamedTemporaryFile()
    FNULL = open(os.devnull, 'w')
    subprocess.run(
        [
            "emacs", "--batch", "-Q", "-l", "~/.emacs-calendar.el",
            "--eval", "(save-fancy-diary '(%d %d %d) %d \"%s\")"
            % (startdate.month, startdate.day, startdate.year,
               (enddate - startdate).days + 1, tf.name)
        ],
        stdout=FNULL, stderr=subprocess.STDOUT)
    retval = []
    current = ["dummy", [], []]
    reo_date = re.compile(r"((?:Saturday|Sunday|Monday|Tuesday|Wednesday|"
                          r"Thursday|Friday)[^:]*)[:\s]*(.*)")
    reo_underline = re.compile(r"^=+$")
    in_header = False
    last_blank = -1
    for count, line in enumerate(tf.readlines()):
        line = line.decode().rstrip()
        if len(line) == 0:  # Line was empty or only whitespace
            last_blank = count
        elif line[0] == "#":  # Line is a tag
            current[2].append(line[1:])
        elif line[0].isspace():  # Line is a continuation
            line = "\n" + line.lstrip()
            if in_header:
                current[1][-1] += line
            else:
                current[-1] += line
        elif mo := reo_date.match(line):  # Line was a date header
            if last_blank != count - 1:
                raise ValueError("Bad header format.")
            in_header = True
            retval.append(current)
            current = [mo.group(1), [], []]
            if mo.group(2):  # ...and had a holiday attached
                current[1].append(mo.group(2))
        elif reo_underline.match(line):  # Line is ====, ending the header
            in_header = False
        else:
            if in_header:  # It's an additional holiday entry
                current[1].append(line)
            else:  # Line is a normal diary entry
                current.append(line)
    retval.append(current)
    del retval[0]  # remove dummy that is appended as first entry
    # replace string date with datetime object
    reo_date = re.compile(r"(\d+)/(\d+)/(\d+)")
    for c, r in enumerate(retval):
        mo = reo_date.search(r[0])
        args = [int(X) for X in reversed(mo.groups())]
        retval[c][0] = datetime.date(*args)
    return retval


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "out_format",
        help="Output format: \t\n"
        "html | htmlyearplan | latex | latexyearplan")
    parser.add_argument(
        "-st", "--start-tomorrow", action='store_true',
        help="Start diary output from tomorrow (latex card only)")
    parser.add_argument(
        "-c", "--card", action='store_true',
        help="Create LaTeX sized for 3\" by 5\" index card")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.out_format == "htmlyearplan":
        startdate = datetime.date.today().replace(day=1)
        enddate = (startdate.replace(year=startdate.year + 1)
                   - datetime.timedelta(days=1))
        print(build_htmlyearplan.build_html_yearplan(
            get_diary(startdate, enddate), startdate, enddate))
    elif args.out_format == "latexyearplan":
        startdate = datetime.date.today().replace(day=1)
        enddate = (startdate.replace(year=startdate.year + 1)
                   - datetime.timedelta(days=1))
        print(build_latexyearplan.build(
            get_diary(startdate, enddate), startdate, enddate))
    elif args.out_format == "html":
        startdate = datetime.date.today()
        startdate -= datetime.timedelta(days=startdate.weekday() + 7)
        enddate = startdate + datetime.timedelta(days=62)
        print(build_html.build_html(
            get_diary(startdate, enddate),
            startdate, enddate))
    elif args.out_format == "latex":
        startdate = datetime.date.today()
        if args.start_tomorrow:
            startdate += datetime.timedelta(days=1)
        enddate = startdate + datetime.timedelta(days=55)
        print(build_latex.build_latex(
            get_diary(startdate, enddate),
            startdate, enddate, args.card))
    elif args.out_format == "debug":
        startdate = datetime.date.today()
        enddate = startdate + datetime.timedelta(days=55)
        for entry in get_diary(startdate, enddate):
            print(entry)
    else:
        print(args.out_format, " is not supported yet.")
