PY := .venv/bin/python
COLLECTIONS := var
NS := chamanswami555.agentia
MODULES := $(notdir $(basename $(wildcard collection/plugins/modules/*.py)))

.PHONY: setup test docs lint sanity integration demo check

# ANSIBLE_CORE=2.17 pins the control node version (CI tests 2.17 and 2.18). The pin goes into the
# same resolve as the requirements, so uv picks an ansible-lint that supports that core version
# (ansible-lint 26.10 refuses ansible-core 2.17; 26.6 accepts it).
ANSIBLE_CORE ?=
setup:
	uv venv --python 3.12 .venv
	uv pip install --python .venv/bin/python -r requirements-dev.txt $(if $(ANSIBLE_CORE),"ansible-core~=$(ANSIBLE_CORE).0",)
	@.venv/bin/python -c 'import ansible.release as r; print("ansible-core", r.__version__)'
	mkdir -p $(COLLECTIONS)/ansible_collections/chamanswami555
	ln -sfn $(CURDIR)/collection $(COLLECTIONS)/ansible_collections/chamanswami555/agentia

# coverage of the modules, the helper and the event source; the floor is a quality gate
test:
	$(PY) -m pytest --cov=collection/plugins --cov=collection/extensions/eda/plugins/event_source --cov-report=term-missing --cov-fail-under=90

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

# ansible-test integration: the targets under collection/tests/integration run the modules against
# the fake CLI shipped inside the collection's tests; same copy-outside-the-repository rule as sanity
INTEGRATION_ROOT ?= /tmp/agentia-integration
integration:
	rm -rf $(INTEGRATION_ROOT) && mkdir -p $(INTEGRATION_ROOT)/ansible_collections/chamanswami555
	rsync -a --exclude __pycache__ --exclude '*.pyc' collection/ $(INTEGRATION_ROOT)/ansible_collections/chamanswami555/agentia/
	cd $(INTEGRATION_ROOT)/ansible_collections/chamanswami555/agentia && $(CURDIR)/.venv/bin/ansible-test integration --local --python 3.12

# the three playbooks and the rulebook against the fake CLI (the rulebook demo needs Java 17)
demo:
	bash tools/demo/offline-demo.sh
	bash tools/demo/offline-rulebook-demo.sh

check: lint test docs
