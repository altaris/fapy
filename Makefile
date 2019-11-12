RUN 		= python3
TYPECHECK	= mypy

all: typecheck unittest

.PHONY: typecheck
typecheck:
	$(TYPECHECK) fapy/*.py

.PHONY: unittest
unittest:
	@$(RUN) -m unittest discover --start-directory tests --pattern "unittest_*.py" --verbose
