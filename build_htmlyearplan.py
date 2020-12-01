import string
import html

main_yearplan_t = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Year planner</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<link rel="stylesheet" type="text/css" href="styles.css"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
</head>
<body id='yearplan'>
<div class="page">
$monthsets
</div>
</body>
</html>
""")

monthset_t = string.Template("""\
$monthset
""")

month_t = string.Template("""\
<div class="month">
<table>
<colgroup><col class="date"/><col class="dayoff" span="3" /><col class="description"/></colgroup>
<thead>
<tr><th colspan="5">$month_name</th></tr>
</thead>
<tbody>
$rows
</tbody>
</table>
</div>
""")

row_t = string.Template("""\
<tr class="$we"><td class="date">$day</td><td class='$jon'></td><td class='$kids'></td><td class='$nscd'></td><td>$entry</td></tr>\
""")


def build_html_yearplan(diary, startdate, enddate):
    months = {}
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        month_id = d[0].replace(day=1) #use first day of month as identifier
        if month_id not in months: months[month_id] = []
        weekend, jon, kids, nscd, entry = ("",) * 5
        if d[0].weekday() >= 5: weekend = "we"
        for e in d[2:]:
            e = html.escape(e)
            if e == "*NTU*": kids = "kids"
            elif e == "*Working*": jon = "jon"
            elif e == "*NSCD*": nscd = "nscd"
            elif (e[0] == "*" and e[-1] == "*"): entry = e[1:-1]
        months[month_id].append(
            row_t.substitute(we=weekend,
                             day=d[0].day,
                             jon=jon,
                             kids=kids,
                             nscd=nscd,
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
