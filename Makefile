all: typecheck unittest

.PHONY: coverage
coverage: unittest
	coverage html
	xdg-open out/coverage/index.html

.PHONY: doc
doc:
	sphinx-build -b html sphinx/ out/doc/
	# xdg-open out/doc/index.html

.PHONY: typecheck
typecheck:
	mypy fapy/*.py

.PHONY: unittest
unittest:
	coverage run -m unittest discover --start-directory tests --pattern "unittest_*.py" --verbose
