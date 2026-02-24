.PHONY: help clean test coverage lint format type-check install install-dev build upload upload-test docs

help:
	@echo "Available commands:"
	@echo "  make install      - Install the package"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make lint         - Run linting (flake8)"
	@echo "  make format       - Format code with black"
	@echo "  make type-check   - Run type checking with mypy"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make build        - Build distribution packages"
	@echo "  make upload-test  - Upload to TestPyPI"
	@echo "  make upload       - Upload to PyPI"
	@echo "  make docs         - Build documentation"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/

coverage:
	pytest tests/ --cov=src/allegro_api --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format:
	black src/ tests/ examples/

type-check:
	mypy src/

build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

docs:
	cd docs && make html

# Development workflow
check: format lint type-check test
	@echo "All checks passed!"

# Before committing
pre-commit: check
	@echo "Ready to commit!"

# Full release process
release: check build
	@echo "Package built and ready for release!"
	@echo "Run 'make upload-test' to test on TestPyPI first"
	@echo "Then run 'make upload' to upload to PyPI"