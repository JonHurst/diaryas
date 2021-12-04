import string
import html

flagged_tags = ("Working", "NTU")

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
<td class='$tag1'></td><td class='$tag2'></td>
<td class='$tag3'></td><td class='org-month-table__defaultentry'>$entry</td>
</tr>\
""")


def build_html_yearplan(diary, startdate, enddate):
    months = {}
    for d in diary:
        if d[0] < startdate:
            continue
        if d[0] > enddate:
            break
        month_id = d[0].replace(day=1)  # use first day of month as identifier
        if month_id not in months:
            months[month_id] = []
        subs = {
            "we": ("org-month-table__day--weekend"
                   if d[0].weekday() >= 5 else ""),
            "day": d[0].day,
            "tag1": "", "tag2": "", "tag3": ""
        }
        entries = []
        for e in d[2]:
            if e in flagged_tags:
                index = flagged_tags.index(e) + 1
                subs[f"tag{index}"] = f"org-month-table__tag{index}"
            else:
                entries.append(html.escape(e))
        subs["entry"] = "; ".join(entries)
        months[month_id].append(row_t.substitute(**subs))
    months_str = ""
    for k in sorted(months.keys()):
        months_str += month_t.substitute(
            month_name=k.strftime("%B %Y"),
            rows="\n".join(months[k]))
    return main_yearplan_t.substitute(months_str=months_str)
