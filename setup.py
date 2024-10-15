# setup.py

import os

from setuptools import find_packages, setup


def get_version():
  """Retrieve the package version from shopipy/__init__.py."""
  with open(os.path.join("shopipy", "__init__.py"), "r", encoding="utf8") as f:
    for line in f:
      if line.startswith("__version__"):
        delim = '"' if '"' in line else "'"
        version = line.split(delim)[1]
        return version
  raise RuntimeError("Unable to find version string in shopipy/__init__.py.")


def read_file(filename):
  """Read a text file and return its contents."""
  with open(filename, "r", encoding="utf8") as f:
    return f.read()


setup(
  name="shopipy",
  version=get_version(),
  description="A CLI tool for managing Shopify orders for print-on-demand products.",
  long_description=read_file("README.md"),
  long_description_content_type="text/markdown",
  author="sjriddle",
  author_email="samuel.riddle1@gmail.com",
  url="https://github.com/sjriddle/shopipy/",
  packages=find_packages(exclude=["tests", ".github"]),
  install_requires=[
    "requests>=2.25.0",
    "rich>=12.6.0",
    "typer[all]>=0.6.1",
    "python-dotenv>=0.20.0",
    "img2pdf>=0.4.4",
    "PyPDF2>=2.10.0",
  ],
  extras_require={
    "test": [
      "pytest>=6.0",
      "pytest-cov>=2.0",
      "ruff>=0.0.261",
      "mypy>=0.910",
      "isort>=5.9",
      "gitchangelog>=3.0.4",
      "mkdocs>=1.2",
      "pytest>=6.2",
      "coverage>=5.5",
      "pytest-cov>=2.12",
    ],
  },
  entry_points={"console_scripts": ["shopipy = shopipy.__main__:main"]},
  classifiers=[
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "License :: OSI Approved :: MIT License",  # Update if using a different license
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Intended Audience :: Product Owners, Developers",
    "Topic :: Utilities",
  ],
  python_requires=">=3.6",
  keywords="shopify cli automation",
  project_urls={
    "Bug Reports": "https://github.com/sjriddle/shopipy/issues",
    "Source": "https://github.com/sjriddle/shopipy/",
  },
)
