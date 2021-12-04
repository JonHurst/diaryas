import string
import re
import html


tags = {"Working": "org-tags__tag1", "NTU": "org-tags__tag2"}

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
<!--h1 class="org-heading org-heading--title">Diary</h1-->
<div class="org-diarypage">
$body
</div>
</body>
</html>
""")

entryblock_t = string.Template("""\
<div class="org-day" id='d$isodate'>
<h2 class='$type'>$date</h2>
$entry_body</div>
""")

entrybody_t = string.Template("""\
<ul class='org-eventlist'>
$entries</ul>
""")

timed_t = string.Template("""\
<span class='org-time'>$timestring</span> $description
""")

entrystring_t = string.Template("""\
<li class='org-eventlist__event $type'>$description</li>
""")


def process_strikethrough(s):
    if s[:3] == "xxx" and s[-3:] == "xxx":
        s = "<del>" + s[3:-3] + "</del>"
    return s


def build_html(diary, startdate, enddate):
    body = "<div class='org-week'>"
    reo_entry = re.compile(
        r"([\d:]{5}(?:-[\d:]{5})?(?:\s\[\w+\])?)\s*(.+)\Z",
        re.DOTALL)
    for d in diary:
        if d[0] < startdate:
            continue
        if d[0] > enddate:
            break
        entries = ""
        for e in d[1]:
            entries += entrystring_t.substitute(
                type="org-eventlist__event--holiday",
                description=html.escape(e))
        if d[2]:  # there are tags
            html_tags = [
                f"<div class=\"{tags.get(X, 'org-tags__default')}\">{X}</div>"
                for X in d[2]]
            entries += f"<li class=\"org-tags\">{''.join(html_tags)}</li>"
        for e in d[3:]:
            e = html.escape(e)
            if mo := reo_entry.match(e):  # timed event
                des = mo.group(2).replace("\n", "<br/> ")
                des = process_strikethrough(des)
                e = timed_t.substitute(
                    timestring=mo.group(1),
                    description=des)
                entry_type = "org-eventlist__event--timed"
            else:
                e = process_strikethrough(e)
                entry_type = "org-eventlist__event--untimed"
            entries += entrystring_t.substitute(
                type=entry_type,
                description=e)
        entrybody = ""
        if len(entries) != 0:
            entrybody = entrybody_t.substitute(entries=entries)
        day = d[0].strftime("%a").lower()
        body += entryblock_t.substitute(
            date=d[0].strftime("%A, %d/%m/%Y"),
            isodate=d[0].strftime("%Y%m%d"),
            type=("org-heading "
                  + "org-heading--weekend" if day in ["sat", "sun"]
                  else "org-heading--weekday"),
            entry_body=entrybody)
        if day == "sun":
            body += "</div><div class='org-week'>"
    body = body[:-len("<div class='org-week'>")]
    return main_t.substitute(body=body)
