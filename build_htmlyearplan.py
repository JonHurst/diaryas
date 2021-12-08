import string
import html

from build_html import build_tags


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
$months_str
</div>
</body>
</html>
""")

month_t = string.Template("""\
<div class="org-month-container">
<table class="org-month-table">
<colgroup>
<col class="org-month-table__datecol"/>
<col class="org-month-table__tagscol"/>
</colgroup>
<thead>
<tr><th class="org-month-table__header" colspan="2">$month_name</th></tr>
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
<td class="org-month-table__tags">$tags</td>
</tr>\
""")


def build_html_yearplan(diary):
    months = {}
    for d in diary:
        month_id = d.date.replace(day=1)  # use first day of month as identifier
        if month_id not in months:
            months[month_id] = []
        subs = {
            "we": ("org-month-table__day--weekend"
                   if d.date.weekday() >= 5 else ""),
            "day": d.date.day,
            "tags": "\n".join(build_tags(d.tags))
        }
        months[month_id].append(row_t.substitute(**subs))
    months_str = ""
    for k in sorted(months.keys()):
        months_str += month_t.substitute(
            month_name=k.strftime("%B %Y"),
            rows="\n".join(months[k]))
    return main_yearplan_t.substitute(months_str=months_str)
