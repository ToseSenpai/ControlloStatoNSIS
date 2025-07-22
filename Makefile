# Makefile for ControlloStatoNSIS

.PHONY: help install install-dev clean test lint format build run deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install production dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  clean       - Clean build artifacts and cache"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black"
	@echo "  build       - Build executable with PyInstaller"
	@echo "  run         - Run the application"
	@echo "  deploy      - Deploy application (clean, test, build, package)"
	@echo "  installer   - Create Windows installer (requires Inno Setup)"
	@echo "  version     - Update version across all files"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Clean build artifacts and cache
clean:
	rmdir /s /q build 2>nul || true
	rmdir /s /q dist 2>nul || true
	rmdir /s /q __pycache__ 2>nul || true
	rmdir /s /q main_window\__pycache__ 2>nul || true
	rmdir /s /q tests\__pycache__ 2>nul || true
	rmdir /s /q .pytest_cache 2>nul || true
	rmdir /s /q .mypy_cache 2>nul || true
	del /s /q *.pyc 2>nul || true
	del /s /q *.pyo 2>nul || true

# Run tests
test:
	pytest tests/ -v

# Run linting checks
lint:
	flake8 main_window/ config.py main.py
	mypy main_window/ config.py main.py --ignore-missing-imports

# Format code with black
format:
	black main_window/ config.py main.py tests/

# Build executable with PyInstaller
build:
	pyinstaller main.spec

# Run the application
run:
	python main.py

# Deploy the application
deploy:
	python deploy_windows.py

# Create Windows installer
installer:
	python deploy.py
	if exist "dist\ControlloStatoNSIS.exe" (
		echo Creating Windows installer...
		if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
			"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_config.iss
			echo Installer created in installer\ directory
		) else (
			echo Inno Setup not found. Please install Inno Setup 6.
		)
	) else (
		echo Build executable first with: make build
	)

# Update version
version:
	@echo Usage: make version VERSION=2.1.0
	@if defined VERSION (
		python update_version.py $(VERSION)
	) else (
		echo Please specify VERSION parameter
		echo Example: make version VERSION=2.1.0
	)

# Setup pre-commit hooks
setup-hooks:
	pre-commit install

# Update pre-commit hooks
update-hooks:
	pre-commit autoupdate

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files 