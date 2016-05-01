def escape(str):
    subs = {"$": r"\$",
            "&": r"\&",
            "%": r"\%",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"$\sim$",
            "^": r"$\wedge$",
            "\\": r"$\backslash$",
            "<": "$<$",
            ">": "$>$"}
    outstr = ""
    open_double_quote = True
    for c in str:
        if c in subs:
            outstr += subs[c]
        elif c == "\"":
            if open_double_quote:
                open_double_quote = False
                outstr += "``"
            else:
                open_double_quote = True
                outstr += "''"
        else:
            outstr += c
    return outstr

if __name__ == "__main__":
    testcase = r"$trouble$%ahead#with{this}~^\statement<>"
    print(testcase)
    print(latex_escape(testcase))
