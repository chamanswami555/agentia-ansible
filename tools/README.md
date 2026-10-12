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
