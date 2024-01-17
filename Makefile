VENV_NAME = .venv
DOCS_AMOUNT = 1000

# Targets
.PHONY: setup main

setup:
	- $(VENV_NAME)/bin/python setup.py

main:
	- $(VENV_NAME)/bin/python main.py $(DOCS_AMOUNT)
