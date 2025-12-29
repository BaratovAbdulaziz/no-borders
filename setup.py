#!/usr/bin/env python3
"""
Setup script for No-Borders KVM Switch
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from package
version = {}
with open(this_directory / "src" / "kvm_switch" / "__init__.py") as f:
    exec(f.read(), version)

setup(
    name="no-borders-kvm",
    version=version.get("__version__", "1.0.0"),
    author=version.get("__author__", "No-Borders"),
    author_email="contact@no-borders.dev",
    description=version.get("__description__", "Cross-platform keyboard and mouse sharing tool"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/no-borders/kvm-switch",
    project_urls={
        "Bug Tracker": "https://github.com/no-borders/kvm-switch/issues",
        "Documentation": "https://github.com/no-borders/kvm-switch/wiki",
        "Source Code": "https://github.com/no-borders/kvm-switch",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pynput>=1.7.6",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "kvm-switch=kvm_switch.__main__:run",
            "no-borders-kvm=kvm_switch.__main__:run",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="kvm, switch, mouse, keyboard, sharing, remote, control, no-borders",
    license="MIT",
)