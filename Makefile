PY := .venv/bin/python
COLLECTIONS := var
NS := chamanswami555.agentia
MODULES := $(notdir $(basename $(wildcard collection/plugins/modules/*.py)))

.PHONY: setup test docs lint sanity demo check

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
	ANSIBLE_COLLECTIONS_PATH=$(COLLECTIONS) $(PY) -m ansiblelint --offline -p collection/playbooks/ collection/extensions/eda/rulebooks/copado_release.yml

# ansible-test wants the collection under ansible_collections/<ns>/<name> as real directories and
# skips every file that Git ignores, so the copy must live outside this repository.
SANITY_ROOT ?= /tmp/agentia-sanity
sanity:
	rm -rf $(SANITY_ROOT) && mkdir -p $(SANITY_ROOT)/ansible_collections/chamanswami555
	rsync -a --exclude __pycache__ --exclude '*.pyc' collection/ $(SANITY_ROOT)/ansible_collections/chamanswami555/agentia/
	cd $(SANITY_ROOT)/ansible_collections/chamanswami555/agentia && $(CURDIR)/.venv/bin/ansible-test sanity --local --requirements --python 3.12

# the three playbooks and the rulebook against the fake CLI (the rulebook demo needs Java 17)
demo:
	bash tools/demo/offline-demo.sh
	bash tools/demo/offline-rulebook-demo.sh

check: lint test docs
