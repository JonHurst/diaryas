import string
import re
import html

main_t = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Diary</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="stylesheet" type="text/css" href="diary.css"/>
</head>
<body>
<div id="diary">
<h1>Diary</h1>
$body
</div>
</body>
</html>
""")

entryblock_t = string.Template("""\
<h2 class='$type'>$date</h2>
$entry_body
""")

entrybody_t = string.Template("""\
<ul class='events'>
$entries</ul>
""")

timed_t = string.Template("""\
<span class='time'>$timestring</span> $description
""")

entrystring_t = string.Template("""\
<li class='$type'>$description</li>
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
            entries += entrystring_t.substitute(type="holiday",
                                                       description=html.escape(e))
        for e in d[2:]:
            e = html.escape(e)
            mo = reo_entry.match(e)
            entry_type = "entry"
            if mo:
                des = mo.group(2).replace("\n", "<br/> ")
                des = process_strikethrough(des)
                e = timed_t.substitute(timestring=mo.group(1),
                                              description=des)
                entry_type = "timed"
            elif e == "*School*":
                e = e[1:-1]
                entry_type = "school"
            elif e == "*Working*":
                e = e[1:-1]
                entry_type = "working"
            elif e == "*NSCD*":
                e = e[1:-1]
                entry_type = "nscd"
            elif e[0] == "*" and e[-1] == "*":
                e = e[1:-1]
                entry_type = "yearplanevent"
            else:
                e = process_strikethrough(e)
            entries += entrystring_t.substitute(type=entry_type,
                                                       description=e)
        entrybody = ""
        if len(entries) != 0:
            entrybody = entrybody_t.substitute(entries=entries)
        body += entryblock_t.substitute(date = d[0].strftime("%A, %d/%m/%Y"),
                                               type="day " + d[0].strftime("%a").lower(),
                                               entry_body=entrybody)
    return main_t.substitute(body=body)
