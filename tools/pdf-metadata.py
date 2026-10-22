"""Set a PDF's document properties to the title and author only, dropping the producer and
creator stamps the print pipeline leaves behind.

Run: .venv-tools/bin/python -I tools/pdf-metadata.py <pdf> "<title>" "<author>"
"""
import sys

from pypdf import PdfReader, PdfWriter

path, title, author = sys.argv[1:4]
reader = PdfReader(path)
writer = PdfWriter()
writer.append(reader)
writer.metadata = None
writer.add_metadata({"/Title": title, "/Author": author})
with open(path, "wb") as handle:
    writer.write(handle)
print(path, {k: str(v) for k, v in (PdfReader(path).metadata or {}).items()})
