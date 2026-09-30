"""
fix_math_escapes.py
Fixes LaTeX backslash escaping in build_comprehensive_report.py
and re-runs it to ensure clean LaTeX equations in both .md and .docx.
"""

with open("build_comprehensive_report.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace single backslash LaTeX commands that conflict with python string escapes:
# \text -> \\text
# \rangle -> \\rangle
# \forall -> \\forall
# \arg -> \\arg
# \Delta -> \\Delta
# \mathcal -> \\mathcal
# \sum -> \\sum
# \max -> \\max
# \min -> \\min
# \le -> \\le
# \ge -> \\ge
# \approx -> \\approx
# \times -> \\times
# \cdot -> \\cdot
# \quad -> \\quad
# \oplus -> \\oplus
# \mathbb -> \\mathbb
# \subseteq -> \\subseteq
# \dots -> \\dots

latex_commands = [
    r"\text", r"\rangle", r"\forall", r"\arg", r"\Delta", r"\mathcal",
    r"\sum", r"\max", r"\min", r"\le", r"\ge", r"\approx", r"\times",
    r"\cdot", r"\quad", r"\oplus", r"\mathbb", r"\subseteq", r"\dots",
    r"\left", r"\right", r"\lfloor", r"\rceil", r"\partial", r"\in",
    r"\notin", r"\emptyset", r"\setminus", r"\sim", r"\to", r"\impliedby"
]

for cmd in latex_commands:
    # replace unescaped cmd with double backslash
    # Note: if it's already double backslashed, avoid making it quadruple
    double_cmd = "\\" + cmd
    text = text.replace(double_cmd, cmd)  # normalize first
    text = text.replace(cmd, double_cmd)  # double escape

with open("build_comprehensive_report.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Successfully fixed LaTeX escapes in build_comprehensive_report.py")
