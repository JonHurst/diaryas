import string
import latex_escape

a4_yearplan_t = string.Template(
r"""\documentclass{article}
\pagestyle{empty}
\usepackage[utf8]{inputenc}
\usepackage{colortbl}
\usepackage{array}
\usepackage[paperwidth=210mm,paperheight=297mm,
tmargin=1.5in, bmargin=.75in, lmargin=5mm, rmargin=5mm]{geometry}

\setlength{\tabcolsep}{0in}
\setlength{\parindent}{0pt}

\newenvironment{monthtable}[1]{%
\scriptsize
\begin{tabular}[t]%
{|>{\centering\hspace{0pt}}p{0.2in}%
  |p{0.1in}%
  |p{0.1in}%
  |>{\raggedright\hspace{0pt}}p{0.75in}|}
\hline
\multicolumn{4}{|c|}{#1}\tabularnewline\hline}
{\end{tabular}}

\newcommand{\dentry}[4]{%
#1&#2&#3&#4\tabularnewline\hline}

\newcommand{\jwork}{\cellcolor{red}}
\newcommand{\kschool}{\cellcolor{green}}
\newcommand{\we}{\rowcolor[gray]{0.8}}

\begin{document}
\raggedright

$months_top

\vspace{10mm}

$months_bot

\end{document}
""")

monthtable_t = string.Template(
    r"""\begin{monthtable}{$month_name}
$month_entries
\end{monthtable}
""")


def build(diary, startdate, enddate):
    months = {}
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        month_id = d[0].replace(day=1) #use first day of month as identifier
        if month_id not in months: months[month_id] = []
        jon, kids, entry = ("{}",) * 3
        day = r"\dentry{" + str(d[0].day) + "}"
        if d[0].weekday() >= 5:
            day = r"\we" + day
        for e in d[2:]:
            e = latex_escape.escape(e)
            if e == "*School*": kids = "\kschool"
            elif e == "*Working*": jon = r"\jwork"
            elif (e[0] == "*" and e[-1] == "*"):
                entry = "{" + e[1:-1] + "}"
        months[month_id].append(day + jon + kids + entry)
    for k in months.keys():
        months[k] = monthtable_t.substitute(month_name=k.strftime("%B %Y"),
                                            month_entries="\n".join(months[k]))
    monthkeys = list(months.keys()); monthkeys.sort()
    months_top = "\hfill".join([months[k] for k in monthkeys[:6]])
    months_bot = "\hfill".join([months[k] for k in monthkeys[6:]])
    return a4_yearplan_t.substitute(months_top=months_top,
                                    months_bot=months_bot)
