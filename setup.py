"""
Setup file for RichCLI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="richcli",
    version="0.1.0",
    author="Apoorva Lal",
    author_email="lal.apoorva@gmail.com",
    description="Terminal User Interface tools for media operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apoorvalal/richcli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "richcli=richcli.main:main",
        ],
    },
)
