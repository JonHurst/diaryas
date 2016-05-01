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
<link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
<h1>Diary</h1>
<div id="diary">
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


def build_html(diary, startdate, enddate):
    body = ""
    reo_entry = re.compile(r"([\d:]{5}[zZ]?(?:-[\d:]{5}[zZ]?)?(?:ish)?)\s*(.+)\Z")
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
                e = timed_t.substitute(timestring=mo.group(1),
                                              description=mo.group(2))
                entry_type = "timed"
            elif e == "*School*":
                e = e[1:-1]
                entry_type = "school"
            elif e == "*Working*":
                e = e[1:-1]
                entry_type = "working"
            elif e[0] == "*" and e[-1] == "*":
                e = e[1:-1]
                entry_type = "yearplanevent"
            elif e[:3] == "xxx" and e[-3:] == "xxx":
                e = e[3:-3]
                entry_type = "strike"
            entries += entrystring_t.substitute(type=entry_type,
                                                       description=e)
        entrybody = ""
        if len(entries) != 0:
            entrybody = entrybody_t.substitute(entries=entries)
        body += entryblock_t.substitute(date = d[0].strftime("%A, %d/%m/%Y"),
                                               type="day " + d[0].strftime("%a").lower(),
                                               entry_body=entrybody)
    return main_t.substitute(body=body)


main_yearplan_t = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Year planner</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body id='yearplan'>
<div class="page">
$monthsets
</div>
</body>
</html>
""")

monthset_t = string.Template("""\
<div class="page">
$monthset
</div>
""")

month_t = string.Template("""\
<div class="month">
<table>
<colgroup><col class="date"/><col class="dayoff" span="2" /><col class="description"/></colgroup>
<thead>
<tr><th colspan="4">$month_name</th></tr>
</thead>
<tbody>
$rows
</tbody>
</table>
</div>
""")

row_t = string.Template("""\
<tr class="$we"><td class="date">$day</td><td class='$jon'></td><td class='$kids'></td><td>$entry</td></tr>\
""")


def build_html_yearplan(diary, startdate, enddate):
    months = {}
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        month_id = d[0].replace(day=1) #use first day of month as identifier
        if month_id not in months: months[month_id] = []
        weekend, jon, kids, entry = ("",) * 4
        if d[0].weekday() >= 5: weekend = "we"
        for e in d[2:]:
            e = html.escape(e)
            if e == "*School*": kids = "kids"
            elif e == "*Working*": jon = "jon"
            elif (e[0] == "*" and e[-1] == "*"): entry = e[1:-1]
        months[month_id].append(
            row_t.substitute(we=weekend,
                             day=d[0].day,
                             jon=jon,
                             kids=kids,
                             entry=entry))
    skeys = list(months.keys()); skeys.sort()
    monthset_keys = [skeys[i:i + 3] for i in range(0, len(skeys), 3)]
    monthsets = ""
    for ms in monthset_keys:
        monthstr = ""
        for m in ms:
            monthstr += month_t.substitute(month_name=m.strftime("%B %Y"),
                                           rows="\n".join(months[m]))
        monthsets += monthset_t.substitute(monthset=monthstr)
    return main_yearplan_t.substitute(monthsets=monthsets)
