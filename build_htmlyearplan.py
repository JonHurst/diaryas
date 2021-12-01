import string
import html

main_yearplan_t = string.Template("""\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
<title>Year planner</title>
<meta charset="UTF-8"/>
<link rel="stylesheet" type="text/css" href="common.css"/>
<link rel="stylesheet" type="text/css" href="yearplan.css"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<link rel="icon" type='image/png' href="https://hursts.org.uk/favicon.png"/>
<script src="yearplan.js"></script>
</head>
<body>
<div class="org-yearplan">
$monthsets
</div>
</body>
</html>
""")

monthset_t = string.Template("""\
$monthset
""")

month_t = string.Template("""\
<div class="org-month-container">
<table class="org-month-table">
<colgroup>
<col class="org-month-table__datecol"/>
<col class="org-month-table__flagcols" span="3" />
<col class="org-month-table__descriptioncol"/>
</colgroup>
<thead>
<tr class="org-month-table__header"><th colspan="5">$month_name</th></tr>
</thead>
<tbody>
$rows
</tbody>
</table>
</div>
""")

row_t = string.Template("""\
<tr class="org-month-table__day $we">
<td class="org-month-table__date">$day</td>
<td class='$jon'></td><td class='$kids'></td>
<td class='$nscd'></td><td>$entry</td>
</tr>\
""")


def build_html_yearplan(diary, startdate, enddate):
    months = {}
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        month_id = d[0].replace(day=1) #use first day of month as identifier
        if month_id not in months: months[month_id] = []
        weekend, jon, kids, nscd, entry = ("",) * 5
        if d[0].weekday() >= 5: weekend = "org-month-table__day--weekend"
        for e in d[2:]:
            e = html.escape(e)
            if e == "*NTU*": kids = "org-month-table__entry--em"
            elif e == "*Working*": jon = "org-month-table__entry--jon"
            elif e == "*NSCD*": nscd = "org-month-table__entry--isla"
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
