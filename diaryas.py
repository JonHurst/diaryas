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


def parse_fancy_diary(str_):
    retval = []
    reo_date = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
    # split string on empty lines to get a list of strings representing days
    days = re.split(r"\n[ \t]*\n", str_)
    for day in days:
        current_day = []
        # split into header and body (body may be empty)
        split = re.split(r"\n={5,}\n", day, 1)
        # split header into lines
        header_lines = [X.rstrip() for X in split[0].splitlines()]
        # first header line may contain a colon in which case there
        # is a holiday to the right of the colon. Any further header
        # lines will be additional holidays
        fields = header_lines[0].split(':')
        mo = reo_date.search(fields[0])
        if not mo:
            raise ValueError("Bad day header.")
        args = [int(X) for X in reversed(mo.groups())]
        current_day.append(datetime.date(*args))
        # append empty list for holidays
        current_day.append([])
        if len(fields) == 2:
            current_day[-1].append(fields[1].strip())
            for holiday in [X.strip() for X in header_lines[1:]]:
                current_day[-1].append(holiday)
        # append empty list to contain tags
        current_day.append([])
        # process the body if it exists
        if len(split) == 2:
            for line in [X.rstrip() for X in split[1].splitlines()]:
                if line[0] == '#':  # line is a tag
                    current_day[2].append(line[1:])
                elif line[0].isspace():  # line is a continuation
                    current_day[-1] += "\n" + line.lstrip()
                else:  # it's a normal diary entry
                    current_day.append(line)
        retval.append(current_day)
    return retval


def get_diary(startdate, enddate, tags_only=False):
    """
    Returns the diary in the form
     [[DATE, [HOLIDAY, ...], [TAG, ...], TEXT, TEXT, ...], ...
    """
    tf = tempfile.NamedTemporaryFile()
    FNULL = open(os.devnull, 'w')
    subprocess.run(
        [
            "emacs", "--batch", "-Q", "-l", "~/.emacs-calendar.el",
            "--eval", "(save-fancy-diary '(%d %d %d) %d \"%s\" %s)"
            % (startdate.month, startdate.day, startdate.year,
               (enddate - startdate).days + 1, tf.name,
               "'t" if tags_only else "nil")
        ],
        stdout=FNULL, stderr=subprocess.STDOUT)
    return parse_fancy_diary(tf.read().decode())


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


def main(args):
    if args.out_format == "htmlyearplan":
        startdate = datetime.date.today().replace(day=1)
        enddate = (startdate.replace(year=startdate.year + 1)
                   - datetime.timedelta(days=1))
        print(build_htmlyearplan.build_html_yearplan(
            get_diary(startdate, enddate, True), startdate, enddate))
    elif args.out_format == "latexyearplan":
        startdate = datetime.date.today().replace(day=1)
        enddate = (startdate.replace(year=startdate.year + 1)
                   - datetime.timedelta(days=1))
        print(build_latexyearplan.build(
            get_diary(startdate, enddate, True), startdate, enddate, args.card))
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


if __name__ == "__main__":
    main(parse_args())
