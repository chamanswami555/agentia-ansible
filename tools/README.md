# Tools

Scripts that build the PDF version of the handbook from its Markdown source.

## Build the handbook PDF

One-time setup (creates a Python environment inside the project; it is ignored by Git):

```sh
cd /Users/chaman/copado-agentia-hackathon
uv venv --python 3.12 .venv-tools
uv pip install --python .venv-tools/bin/python markdown
```

Build:

```sh
cd /Users/chaman/copado-agentia-hackathon
.venv-tools/bin/python -I tools/md2html.py docs/hackathon-handbook.md var/hackathon-handbook.html "Copado Agentia Headless Hackathon: Project Handbook"
node tools/html2pdf.mjs "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" "$PWD/var/hackathon-handbook.html" docs/hackathon-handbook.pdf "" "Copado Agentia Headless Hackathon: Project Handbook"
```

`var/` holds build intermediates and is ignored by Git. Any Chromium-family browser works in place of Brave (for example Google Chrome).

To render one page as an image for a visual check on macOS:

```sh
node tools/html2pdf.mjs "<browser>" "$PWD/var/hackathon-handbook.html" var/page-23.pdf 23
qlmanage -t -s 1400 -o var var/page-23.pdf
```

## Other documents

The deck is `docs/deck/agentia-ansible-deck.html`, printed as a 16:9 PDF with the same tool:

```sh
PDF_PAPER_WIDTH=13.33 PDF_PAPER_HEIGHT=7.5 PDF_MARGIN=0 PDF_FOOTER=off \
  node tools/html2pdf.mjs "<browser>" "$PWD/docs/deck/agentia-ansible-deck.html" docs/agentia-ansible-deck.pdf
```

`PDF_PAPER_WIDTH` and `PDF_PAPER_HEIGHT` are inches (default A4 portrait), `PDF_MARGIN` sets all four
margins, `PDF_FOOTER=off` drops the page footer.

The project document is built with the Python document library (`uv pip install --python .venv-tools/bin/python python-docx`):

```sh
.venv-tools/bin/python -I tools/build-project-doc.py   # writes docs/agentia-ansible-project.docx
```

`tools/quality-gates/agentia_quality_gates.sh` is the local quality gate for Copado Source Format
projects; copy it to a project root as `.agentia_quality_gates.sh`.

## Document properties

After any PDF build, set the properties to the title and the owner's name only (the print
pipeline otherwise stamps its producer and the browser's user agent):

```sh
.venv-tools/bin/python -I tools/pdf-metadata.py docs/agentia-ansible-deck.pdf "agentia-ansible" "Chaman Swami"
.venv-tools/bin/python -I tools/pdf-metadata.py docs/hackathon-handbook.pdf "Copado Agentia Headless Hackathon: Project Handbook" "Chaman Swami"
```

`tools/build-project-doc.py` sets the same properties on the .docx (author, title, subject).
