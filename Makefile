PY := .venv/bin/python
COLLECTIONS := var
NS := chamanswami555.agentia
MODULES := $(notdir $(basename $(wildcard collection/plugins/modules/*.py)))

.PHONY: setup test docs lint check

setup:
	uv venv --python 3.12 .venv
	uv pip install --python .venv/bin/python -r requirements-dev.txt
	mkdir -p $(COLLECTIONS)/ansible_collections/chamanswami555
	ln -sfn $(CURDIR)/collection $(COLLECTIONS)/ansible_collections/chamanswami555/agentia

test:
	$(PY) -m pytest

docs:
	@for m in $(MODULES); do \
	  ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS) $(PY) -m ansible.cli.doc -t module $(NS).$$m > /dev/null && echo "doc ok: $$m" || exit 1; \
	done

lint:
	$(PY) -m pyflakes collection/plugins collection/tests tools/fake-agentia/agentia

check: lint test docs
