import string
import re
import latex_escape

a4diary_t = string.Template(
r"""\documentclass{article}
\pagestyle{empty}

\usepackage{fontspec}
\newfontfamily{\symbolfont}{Symbola}
\usepackage{ucharclasses}
\setTransitionsForSymbols{\symbolfont}{}

\usepackage[dvipsnames]{xcolor}
\usepackage{ulem}
\usepackage[paper=a4paper,
tmargin=0.75in, bmargin=0.75in, lmargin=0.25in, rmargin=0.25in]{geometry}
\setlength\parindent{0pt}

\newcommand{\event}[1]{\vspace{1mm}\small #1\\}

\newcommand{\timedevent}[2]{%
  \vspace{1mm}\small\textbf{#1}\\
  \hspace{1em}#2\\}

\newcommand{\diaryday}[2]{%
  \vbox{\raggedright{\bf #1}\\
  #2}

\vspace{10mm plus 50mm minus 5mm}}

\usepackage{multicol}
\begin{document}
\begin{multicols}{3}
$body
\end{multicols}
\end{document}
""")

carddiary_t = string.Template(
r"""\documentclass{article}
\pagestyle{empty}
\usepackage[utf8]{inputenc}
\usepackage[dvipsnames]{xcolor}
\usepackage{ulem}
\usepackage[paperwidth=3in,paperheight=5in,
tmargin=0.25in, bmargin=0.55in, lmargin=0.25in, rmargin=0.25in]{geometry}
\setlength\parindent{0pt}
\raggedbottom
\newcommand{\event}[1]{\vspace{0.5mm}\small #1\\}

\newcommand{\timedevent}[2]{%
  \vspace{0.5mm}{\small\textbf{#1}\nopagebreak\\
  \hspace{1em}#2\\}}

\newcommand{\diaryday}[2]{%
  \vbox{\raggedright{\bf #1}\\
  #2}

\vspace{3mm}}

\begin{document}
$body
\end{document}
""")

diaryday_t = string.Template(
r"""\diaryday{\textcolor{$color}{$date}}{
$events}

""")

holiday_event_t = string.Template(
r"""\event{\textit{$e}}
""")

std_event_t = string.Template(
r"""\event{$$\bullet$$ $e}
""")

timed_event_t = string.Template(
r"""\timedevent{$timestring}{$description}
""")

school_t = r"\fcolorbox{black}{green}{\strut NTU}"
working_t = r"\fcolorbox{black}{red}{\strut Working}"
notworking_t = r"\fcolorbox{black}{white}{\strut Not Working}"
nscd_t = r"\fcolorbox{black}{SkyBlue}{\strut NSCD}"
flags_t = string.Template("\\event{$working $school $nscd}\n")


def process_strikethrough(s):
    if s[:3] == "xxx" and s[-3:] == "xxx":
        s = r"\sout{" + s[3:-3] + "}"
    return s


def build_latex(diary, startdate, enddate, card=False):
    body = ""
    reo_entry = re.compile(r"([\d:]{5}(?:-[\d:]{5})?(?:\s\[\w+\])?)\s*(.+)\Z", re.DOTALL)
    for d in diary:
        if d[0] < startdate: continue
        if d[0] > enddate: break
        holidays = []
        for e in d[1]: #holidays
            e = latex_escape.escape(e)
            holidays.append(holiday_event_t.substitute(e=e))
        school_p, working_p, nscd_p = False, False, False
        events = []
        for e in d[2:]:
            e = latex_escape.escape(e)
            if e == "*NTU*": school_p = True
            elif e == "*Working*": working_p = True
            elif e == "*NSCD*": nscd_p = True
            elif (e[0] == "*" and e[-1] == "*"):
                events.append(std_event_t.substitute(e="\\textbf{" + e[1:-1] + "}"))
            else:
                mo = reo_entry.match(e)
                if mo:
                    ts = mo.group(1)
                    de = mo.group(2)
                    de = de.replace("\n", r"\\\hspace{1em}")
                    de = process_strikethrough(de)
                    events.append(timed_event_t.substitute(timestring=ts,
                                                           description=de))
                else:
                    e = process_strikethrough(e)
                    events.append(std_event_t.substitute(e=e))
        flags = flags_t.substitute(working=working_t if working_p else notworking_t,
                                   school=school_t if school_p else "",
                                   nscd=nscd_t if nscd_p else "")
        body += diaryday_t.substitute(
            color="black",
            date=d[0].strftime("%A, %d/%m/%Y"),
            events = "".join(holidays) + flags + "".join(events))
    main_t = carddiary_t if card else a4diary_t
    return main_t.substitute(body=body)
