import string
import re
import latex_escape

a4diary_t = string.Template(r"""
\documentclass{article}
\pagestyle{empty}

\usepackage{fontspec}
\newfontfamily{\symbolfont}{Symbola}
\usepackage{ucharclasses}
\setTransitionsForSymbols{\symbolfont}{}

\usepackage[dvipsnames]{xcolor}
\usepackage{ulem}
\usepackage[paper=a4paper,
tmargin=0.75in, bmargin=1.5in, lmargin=0.25in, rmargin=0.25in]{geometry}
\setlength\parindent{0pt}

\newcommand{\event}[1]{\vspace{1mm}\small #1\\}

\newcommand{\timedevent}[2]{%
  \vspace{1mm}\small\textbf{#1}\\
  \hspace{1em}#2\\}

\newcommand{\diaryday}[2]{%
  \vbox{\raggedright{\bf #1}\\
  #2}

\vspace{1in plus 0.5in minus 0.1in}}

\usepackage{multicol}
\begin{document}
\begin{multicols}{3}
$body
\end{multicols}
\end{document}
""")

carddiary_t = string.Template(r"""
\documentclass{article}
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

diaryday_t = string.Template(r"""
\diaryday{\textcolor{$color}{$date}}{
$events}

""")

holiday_event_t = string.Template(r"""
\event{\textit{$e}}
""")

std_event_t = string.Template(r"""
\event{$$\bullet$$ $e}
""")

timed_event_t = string.Template(r"""
\timedevent{$timestring}{$description}
""")

tag1_t = string.Template(r"\fcolorbox{black}{red}{\strut $contents}")
tag2_t = string.Template(r"\fcolorbox{black}{green}{\strut $contents}")
tag3_t = string.Template(r"\fcolorbox{black}{SkyBlue}{\strut $contents}")
gentag_t = string.Template(r"\fcolorbox{black}{white}{\strut $contents}")
notworking_t = r"\fcolorbox{black}{white}{\strut Not Working}"
flags_t = string.Template("\\event{$flags}\n")


def process_strikethrough(s):
    if s[:3] == "xxx" and s[-3:] == "xxx":
        s = r"\sout{" + s[3:-3] + "}"
    return s


def build_latex(diary, card=False):
    body = ""
    for d in diary:
        holidays = []
        for e in d.holidays:  # holidays
            e = latex_escape.escape(e)
            holidays.append(holiday_event_t.substitute(e=e))
        events = []
        for e in d.entries:
            de = latex_escape.escape(e.text)
            de = de.replace("\n", r"\\\hspace{1em}")
            de = process_strikethrough(de)
            if e.timestr:
                ts = latex_escape.escape(e.timestr)
                events.append(
                    timed_event_t.substitute(timestring=ts, description=de))
            else:
                events.append(std_event_t.substitute(e=de))
        flag_lookup = {"Working": tag1_t, "NTU": tag2_t}
        flags = [flag_lookup.get(X, gentag_t).substitute(contents=X)
                 for X in d.tags]
        if "Working" not in d.tags:
            flags.append(notworking_t)
        flag_str = flags_t.substitute(flags=" ".join(flags))
        body += diaryday_t.substitute(
            color="black",
            date=d.date.strftime("%A, %d/%m/%Y"),
            events="".join(holidays) + flag_str + "".join(events))
    main_t = carddiary_t if card else a4diary_t
    return main_t.substitute(body=body)
