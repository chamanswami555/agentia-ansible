"""Convert a Markdown document to a print-ready HTML file (A4 styling).

Usage: python tools/md2html.py <input.md> <output.html> "<title>"
Requires the Python-Markdown package (see tools/README.md).
"""
import html
import sys

import markdown

src, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(src, encoding="utf-8").read()
body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
css = """
@page { size: A4; margin: 14mm 13mm 16mm 13mm; }
html { -webkit-print-color-adjust: exact; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.38; color: #111; margin: 0; }
h1 { font-size: 17pt; margin: 0 0 10pt 0; }
h2 { font-size: 13.5pt; margin: 18pt 0 8pt 0; padding-top: 6pt; border-top: 1px solid #bbb; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 6pt 0; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 10pt 0 5pt 0; break-after: avoid; }
p { margin: 0 0 6pt 0; }
ul, ol { margin: 0 0 6pt 0; padding-left: 18pt; }
li { margin: 0 0 2pt 0; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 10pt 0; font-size: 8.6pt; line-height: 1.3; }
th, td { border: 0.5pt solid #999; padding: 3pt 5pt; vertical-align: top; text-align: left; overflow-wrap: anywhere; }
th { background: #e9e9e9; white-space: nowrap; }
tr { break-inside: avoid; }
code { font-family: Menlo, Courier, monospace; font-size: 8.4pt; background: #f2f2f2; padding: 0 2pt; overflow-wrap: anywhere; }
pre { font-family: Menlo, Courier, monospace; font-size: 8.4pt; background: #f2f2f2; padding: 6pt; white-space: pre-wrap; overflow-wrap: anywhere; border: 0.5pt solid #ccc; }
a { color: #0b4f9c; text-decoration: none; overflow-wrap: anywhere; }
"""
doc = (
    "<!doctype html><html><head><meta charset='utf-8'><title>"
    + html.escape(title)
    + "</title><style>"
    + css
    + "</style></head><body>"
    + body
    + "</body></html>"
)
open(out, "w", encoding="utf-8").write(doc)
print("html written:", out, len(doc), "bytes; tables:", body.count("<table>"), "; h2:", body.count("<h2>"))
