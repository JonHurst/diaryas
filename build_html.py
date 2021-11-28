import string
import re
import html

main_t = string.Template("""\
<html xmlns="http://www.w3.org/1999/xhtml">
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
<div class="org-page">
<h1 class="org-heading org-heading--title">Diary</h1>
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
    body = ""
    reo_entry = re.compile(r"([\d:]{5}(?:-[\d:]{5})?(?:\s\[\w+\])?)\s*(.+)\Z", re.DOTALL)
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        entries = ""
        for e in d[1]:
            entries += entrystring_t.substitute(type="org-eventlist__event--holiday",
                                                       description=html.escape(e))
        for e in d[2:]:
            e = html.escape(e)
            mo = reo_entry.match(e)
            entry_type = "org-eventlist__event--untimed"
            if mo:
                des = mo.group(2).replace("\n", "<br/> ")
                des = process_strikethrough(des)
                e = timed_t.substitute(timestring=mo.group(1),
                                              description=des)
                entry_type = "org-eventlist__event--timed"
            elif e == "*NTU*":
                e = e[1:-1]
                entry_type = "org-eventlist__event--ntu"
            elif e == "*Working*":
                e = e[1:-1]
                entry_type = "org-eventlist__event--working"
            elif e == "*NSCD*":
                e = e[1:-1]
                entry_type = "org-eventlist__event--nscd"
            elif e[0] == "*" and e[-1] == "*":
                e = e[1:-1]
                entry_type = "org-eventlist__event--yearplanevent"
            else:
                e = process_strikethrough(e)
            entries += entrystring_t.substitute(type=entry_type,
                                                       description=e)
        entrybody = ""
        if len(entries) != 0:
            entrybody = entrybody_t.substitute(entries=entries)
        day = d[0].strftime("%a").lower()
        body += entryblock_t.substitute(
            date = d[0].strftime("%A, %d/%m/%Y"),
            isodate = d[0].strftime("%Y%m%d"),
            type="org-heading " +
            ("org-heading--weekend" if day  in ["sat", "sun"]
             else "org-heading--weekday"),
            entry_body=entrybody)
        if day in ["sun", "fri"]:
            body += "<hr class='org-weekseparator'/>"
    return main_t.substitute(body=body)
