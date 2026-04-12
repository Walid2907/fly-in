PYTHON = python3
MAIN = main.py

# Default target
all: run


# Install project dependencies
install:
	pip install -r requirements.txt

# Run the project
run:
	@$(PYTHON) $(MAIN)

# Debug mode
debug:
	@$(PYTHON) -m pdb $(MAIN)

# Lint code
lint:
	@$(PYTHON) -m flake8 .
	@$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@$(PYTHON) -m flake8 .
	@$(PYTHON) -m mypy . --strict

build:
	@$(PYTHON) -m pip install --quiet --upgrade build
	@$(PYTHON) -m build
	@cp dist/mazegen-*.whl . 2>/dev/null || true
	@cp dist/mazegen-*.tar.gz . 2>/dev/null || true
# Clean python cache files
clean:
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type d -name ".mypy_cache" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "*.egg-info" -exec rm -r {} +
	@rm -rf dist/ build/
	@rm -rf *.egg-info
	@rm -rf .idea

.PHONY: all install run debug lint lint-strict clean build