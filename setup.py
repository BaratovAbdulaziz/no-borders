"""
Setup script for No-Borders KVM Switch
"""
from setuptools import setup, find_packages
import os

# Read version from config
version = "1.2.0"  # Default version
try:
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'kvm_switch', 'utils', 'config.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('APP_VERSION'):
                version = line.split('=')[1].strip().strip('"')
                break
except FileNotFoundError:
    pass  # Use default version

# Read README
readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_file, 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_file, 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="no-borders-kvm",
    version=version,
    author="No-Borders Team",
    author_email="support@no-borders.com",
    description="Seamless Multi-Computer Control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/no-borders/no-borders-kvm",
    project_urls={
        "Bug Tracker": "https://github.com/no-borders/no-borders-kvm/issues",
        "Documentation": "https://github.com/no-borders/no-borders-kvm/wiki",
        "Source Code": "https://github.com/no-borders/no-borders-kvm",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kvm-switch=kvm_switch.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="kvm switch remote control multi-computer seamless",
    license="MIT",
)