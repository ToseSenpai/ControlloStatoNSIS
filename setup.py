#!/usr/bin/env python3
# setup.py
# Setup script for ControlloStatoNSIS

from setuptools import setup, find_packages
from version import get_version, get_version_info

# Read the README file
with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="controllo-stato-nsis",
    version=get_version(),
    author=get_version_info()["author"],
    author_email=get_version_info()["email"],
    description=get_version_info()["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ControlloStatoNSIS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "pytest-cov>=4.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "controllo-stato-nsis=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ico", "*.png", "*.ttf", "*.ttc", "*.svg"],
    },
    keywords="nsis, automation, excel, web, desktop, gui, pyqt6",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ControlloStatoNSIS/issues",
        "Source": "https://github.com/yourusername/ControlloStatoNSIS",
        "Documentation": "https://github.com/yourusername/ControlloStatoNSIS/tree/main/docs",
    },
) 