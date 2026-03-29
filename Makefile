VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PROMPT = snoa

.PHONY: wheel clean venv test test-unit test-integration

venv: $(VENV)/bin/activate

$(VENV)/bin/activate:
	python3 -m venv --prompt $(PROMPT) $(VENV)
	$(PIP) install --upgrade pip wheel
	$(PIP) install -e ".[dev]"

wheel: venv
	$(PYTHON) -m build --wheel

test: test-unit

test-unit: venv
	$(PYTHON) -m pytest tests/ -v --ignore=tests/test_integration.py

test-integration: venv
	$(PYTHON) -m pytest tests/test_integration.py -v

clean:
	rm -rf dist/ build/ *.egg-info satnogs_network_api/*.egg-info
