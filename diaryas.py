#!/usr/bin/python3

import os
import subprocess
import argparse
import tempfile
import datetime
import re
from typing import Tuple, List

from diarytypes import DayRecord, Entry
import build_html
import build_htmlyearplan
import build_latex
import build_latexyearplan


def _parse_header(str_: str) -> Tuple[datetime.date, Tuple[str, ...]]:
    """ Parses the header part of a fancy diary day.

    :param str_: The string containing the header part
    :return: A tuple with the date in the first field, and a tuple of holidays
        in the second.
    """
    reo_date = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
    header_lines = [X.rstrip() for X in str_.splitlines()]
    # first header line may contain a colon in which case there
    # is a holiday to the right of the colon. Any further header
    # lines will be additional holidays
    fields = header_lines[0].split(':')
    mo = reo_date.search(fields[0])
    if not mo:
        raise ValueError("Bad day header.")
    args = [int(X) for X in reversed(mo.groups())]
    date = datetime.date(*args)
    # append empty list for holidays
    holidays: List[str] = []
    if len(fields) == 2:
        holidays.append(fields[1].strip())
        for holiday in [X.strip() for X in header_lines[1:]]:
            holidays.append(holiday)
    return (date, tuple(holidays))


def _parse_body(str_: str) -> Tuple[Tuple[str, ...], Tuple[Entry, ...]]:
    """ Parses the body part of a fancy diary entry.

    :param str_: The string containing the body part.
    :return: A tuple, the first field of which is a tuple of tag strings, and
        the second a tuple of Entry tuples.
    """
    reo_timestr = re.compile(r"[\d:]{5}(?:-[\d:]{5})?")
    tags: List[str] = []
    entries: List[Entry] = []
    for line in [X.rstrip() for X in str_.splitlines()]:
        if line[0] == '#':  # line is a tag
            tags.append(line[1:])
        elif line[0].isspace():  # line is a continuation
            if not entries:
                raise ValueError("Bad continuation.")
            entries[-1] = Entry(entries[-1].timestr,
                                entries[-1].text + "\n" + line.lstrip())
        else:  # it's a normal diary entry
            mo = reo_timestr.match(line)
            if mo:  # it has a time string
                timestr = mo.group(0)
                rest = line[len(timestr):].strip()
                entries.append(Entry(timestr, rest))
            else:
                entries.append(Entry(None, line))
    return (tuple(tags), tuple(entries))


def parse_fancy_diary(str_: str) -> Tuple[DayRecord, ...]:
    """ Parse the fancy diary as a string into a tuple of DayRecord objects.

    :param str_: The fancy diary in string form.
    :return: The diary as a tuple of DayRecord objects
    """
    retval: List[DayRecord] = []
    # split string on empty lines to get a list of strings representing days
    days = re.split(r"\n[ \t]*\n", str_)
    for day in days:
        # split into header and body (body may be empty)
        # note that splitting into days may have removed terminating new line
        # if there is a holiday but no tags or entries.
        split = re.split(r"\n={5,}\n?", day, 1)
        date, holidays = _parse_header(split[0])
        # process the body if it exists
        if len(split) == 2:
            tags, entries = _parse_body(split[1])
            retval.append(DayRecord(date, holidays, tags, entries))
        else:
            retval.append(DayRecord(date, holidays, (), ()))
    return tuple(retval)


def get_diary(
        startdate: datetime.date,
        enddate: datetime.date,
        tags_only: bool = False) -> str:
    """ Get the fancy diary from emacs as a string.

    :param startdate: First date of interest
    :param enddate: Last date of interest
    :tags_only: Whether to only process tags (e.g. for yearplans)
    :return: The fancy diary as a string.
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
    return tf.read().decode()


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
            parse_fancy_diary(get_diary(startdate, enddate, True))))
    elif args.out_format == "latexyearplan":
        startdate = datetime.date.today().replace(day=1)
        enddate = (startdate.replace(year=startdate.year + 1)
                   - datetime.timedelta(days=1))
        print(build_latexyearplan.build(
            parse_fancy_diary(
                get_diary(startdate, enddate, True))))
    elif args.out_format == "html":
        startdate = datetime.date.today()
        startdate -= datetime.timedelta(days=startdate.weekday() + 7)
        enddate = startdate + datetime.timedelta(days=62)
        print(build_html.build_html(
            parse_fancy_diary(
                get_diary(startdate, enddate))))
    elif args.out_format == "latex":
        startdate = datetime.date.today()
        if args.start_tomorrow:
            startdate += datetime.timedelta(days=1)
        enddate = startdate + datetime.timedelta(days=55)
        print(build_latex.build_latex(
            parse_fancy_diary(get_diary(startdate, enddate)),
            args.card))
    elif args.out_format == "debug":
        startdate = datetime.date.today()
        enddate = startdate + datetime.timedelta(days=55)
        for entry in parse_fancy_diary(get_diary(startdate, enddate)):
            print(entry)
    else:
        print(args.out_format, " is not supported yet.")


if __name__ == "__main__":
    main(parse_args())
