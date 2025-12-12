PY_FILES=$(wildcard *.py)

all: tags mypy

tags: $(PY_FILES)
	ctags $(PY_FILES)

.PHONY: mypy
mypy: $(PY_FILES)
	mypy $(PY_FILES)
