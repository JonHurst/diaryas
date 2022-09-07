import string
import html
from typing import Tuple

from diarytypes import DayRecord


special_tags = ("Working", "NTU")


main_t = string.Template("""\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<title>Diary</title>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" type="text/css" href="common.css"/>
<link rel="stylesheet" type="text/css" href="diary.css"/>
<link rel="icon" type='image/png' href="https://hursts.org.uk/images/diary.png"/>
<script src="diary.js"></script>
</head>

<body>
<div class="org-diarypage">
$body
</div>
<div id="refreshed"> - </div>
</body>
</html>
""")

entryblock_t = string.Template("""\
<div class="org-day" id='d$isodate'>
<h2 class='$type'>$date</h2>
$body
</div>
""")


def process_strikethrough(s: str) -> str:
    if s[:3] == "xxx" and s[-3:] == "xxx":
        s = "<del>" + s[3:-3] + "</del>"
    return s


def modifier_from_tag(tag: str) -> str:
    try:
        return f" org-tags__tag--{special_tags.index(tag) + 1}"
    except ValueError:
        return ""


def build_tags(taglist):
    tags = [html.escape(X) for X in taglist]
    tags.sort(key=lambda a: a not in special_tags)
    return [f"<div class=\"org-tags__tag{modifier_from_tag(X)}\">{X}</div>"
            for X in tags]


def build_html(diary: Tuple[DayRecord]) -> str:
    body = "<div class='org-week'>\n"
    for rec in diary:
        day_body = []
        if rec.tags:
            html_tags = build_tags(rec.tags)
            day_body.append(
                '<div class="org-tags">\n'
                + ''.join(html_tags)
                + "\n</div>")
        if rec.holidays:
            entries = ""
            for hol in rec.holidays:
                entries += (
                    "<li class='org-holidays__entry'>"
                    + html.escape(hol)
                    + "</li>\n")
            day_body.append(
                "<ul class='org-holidays'>\n"
                + entries
                + "</ul>")
        timed_events, untimed_events = [], []
        for e in rec.entries:
            text = html.escape(e.text)
            text = text.replace("\n", " <br/>")
            text = process_strikethrough(text)
            if e.timestr:
                timestr = (f"<span class='org-time'>"
                           f"{html.escape(e.timestr)}</span> ")
                timed_events.append(
                    f"<li class='org-timed__event'>"
                    f"{timestr}{text}</li>")
            else:
                untimed_events.append(
                    f"<li class='org-untimed__event'>"
                    f"{text}</li>")
        if untimed_events:
            untimed_body = "\n".join(untimed_events)
            day_body.append(f"<ul class='org-untimed'>\n{untimed_body}\n</ul>")
        if timed_events:
            timed_body = "\n".join(timed_events)
            day_body.append(f"<ul class='org-timed'>\n{timed_body}\n</ul>")
        day = rec.date.strftime("%a").lower()
        body += entryblock_t.substitute(
            date=rec.date.strftime("%A, %d/%m/%Y"),
            isodate=rec.date.strftime("%Y%m%d"),
            type=("org-heading "
                  + ("org-heading--weekend" if day in ["sat", "sun"]
                     else "org-heading--weekday")),
            body="\n".join(day_body))
        if day == "sun":
            body += "</div><div class='org-week'>\n"
    body = body[:-len("<div class='org-week'>\n")]
    return main_t.substitute(body=body)
