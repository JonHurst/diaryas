import string
import latex_escape

a4_yearplan_t = string.Template(r"""
\documentclass{article}
\pagestyle{empty}

\usepackage{colortbl}
\usepackage{array}
\usepackage[dvipsnames]{xcolor}
\usepackage[paperwidth=297mm,paperheight=210mm,
tmargin=0.5in, bmargin=0.5in, lmargin=0.5in, rmargin=0.5in]{geometry}
\usepackage{tcolorbox}

\setlength{\tabcolsep}{0in}
\setlength{\parindent}{0pt}

\newenvironment{monthtable}[1]{%
\scriptsize
\begin{tabular}[t]%
{|>{\centering}m{0.2in}|>{\raggedright}m{1.5in}|}
\hline
\multicolumn{2}{|c|}{#1}\tabularnewline\hline}
{\end{tabular}}

\newcommand{\dentry}[2]{%
#1&#2\tabularnewline\hline}

\newcommand{\diarytag}[2]{%
\hspace*{0.5mm}\tcbox[colback=#1]{\strut #2}\linebreak[0]}

\newcommand{\we}{\rowcolor[gray]{0.8}}

\renewcommand{\arraystretch}{1.75}

\begin{document}
\tcbset{tcbox raise base,valign=center,nobeforeafter,
boxrule=0.2mm,boxsep=0mm,left=0.5mm,right=0.5mm,top=0.75mm,bottom=0mm,middle=0mm,arc=0.5mm}
\raggedright

$months_top

\pagebreak

$months_bot

\end{document}
""")


monthtable_t = string.Template(r"""
\begin{monthtable}{$month_name}
$month_entries
\end{monthtable}
""")

tag1_t = string.Template(r"\diarytag{red}{$contents}")
tag2_t = string.Template(r"\diarytag{green}{$contents}")
tag3_t = string.Template(r"\diarytag{SkyBlue}{$contents}")
gentag_t = string.Template(r"\diarytag{white}{$contents}")

FLAG_LOOKUP = {"Working": tag1_t, "NTU": tag2_t}


def build(diary):
    months = {}
    for d in diary:
        month_id = d.date.replace(day=1)  # use first day of month as key
        if month_id not in months:
            months[month_id] = []
        we = r"\we" if d.date.weekday() >= 5 else ""
        taglist = []
        for e in sorted(d.tags, key=lambda a: a not in FLAG_LOOKUP):
            taglist.append(FLAG_LOOKUP.get(e, gentag_t).substitute(
                contents=latex_escape.escape(e)))
        months[month_id].append(
            f"{we}\\dentry{{{str(d.date.day)}}}{{{''.join(taglist)}}}")
    for k in months.keys():
        months[k] = monthtable_t.substitute(month_name=k.strftime("%B %Y"),
                                            month_entries="\n".join(months[k]))
    monthkeys = sorted(months.keys())
    months_top = r"\hfill".join([months[k] for k in monthkeys[:6]])
    months_bot = r"\hfill".join([months[k] for k in monthkeys[6:]])
    return a4_yearplan_t.substitute(months_top=months_top,
                                    months_bot=months_bot)
