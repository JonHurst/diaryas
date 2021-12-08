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
<link rel="icon" type='image/png' href="https://hursts.org.uk/favicon.png"/>
<script src="diary.js"></script>
</head>

<body>
<div class="org-diarypage">
$body
</div>
</body>
</html>
""")

entryblock_t = string.Template("""\
<div class="org-day" id='d$isodate'>
<h2 class='$type'>$date</h2>
<ul class='org-eventlist'>
$entry_body</ul>
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


def build_html(diary: Tuple[DayRecord]) -> str:
    body = "<div class='org-week'>\n"
    for rec in diary:
        entries = ""
        for hol in rec.holidays:
            entries += (
                "<li class='org-eventlist__event "
                + "org-eventlist__event--holiday'>"
                + html.escape(hol)
                + "</li>\n")
        if rec.tags:
            tags = [html.escape(X) for X in rec.tags]
            tags.sort(key=lambda a: a not in special_tags)
            html_tags = [
                f"<div class=\"org-tags__tag{modifier_from_tag(X)}\">{X}</div>"
                for X in tags]
            entries += (
                '<li class="org-eventlist__taglist"><div class="org-tags">\n'
                + '\n'.join(html_tags)
                + "\n</div></li>\n")
        for e in rec.entries:
            timestr = (
                f"<span class='org-time'>{html.escape(e.timestr)}</span> "
                if e.timestr else "")
            entry_type = (
                "org-eventlist__event--timed"
                if e.timestr else "org-eventlist__event--untimed")
            text = html.escape(e.text)
            text = text.replace("\n", " <br/>")
            text = process_strikethrough(text)
            entries += (f"<li class='org-eventlist__event {entry_type}'>"
                        f"{timestr}{text}</li>\n")
        day = rec.date.strftime("%a").lower()
        body += entryblock_t.substitute(
            date=rec.date.strftime("%A, %d/%m/%Y"),
            isodate=rec.date.strftime("%Y%m%d"),
            type=("org-heading "
                  + ("org-heading--weekend" if day in ["sat", "sun"]
                     else "org-heading--weekday")),
            entry_body=entries)
        if day == "sun":
            body += "</div><div class='org-week'>\n"
    body = body[:-len("<div class='org-week'>\n")]
    return main_t.substitute(body=body)
