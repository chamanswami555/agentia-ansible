PY := .venv/bin/python
COLLECTIONS := var
NS := chamanswami555.agentia

.PHONY: setup test docs lint

setup:
	uv venv --python 3.12 .venv
	uv pip install --python .venv/bin/python -r requirements-dev.txt
	mkdir -p $(COLLECTIONS)/ansible_collections/chamanswami555
	ln -sfn $(CURDIR)/collection $(COLLECTIONS)/ansible_collections/chamanswami555/agentia

test:
	$(PY) -m pytest

docs:
	ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS) $(PY) -m ansible.cli.doc -t module $(NS).agentia_work

lint:
	$(PY) -m pyflakes collection/plugins tools/fake-agentia/agentia || true
