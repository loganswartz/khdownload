#!/usr/bin/env python3

import setuptools


with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="khdownload",
    version="0.1.0",
    author="Logan Swartzendruber",
    author_email="logan.swartzendruber@gmail.com",
    description="Automatically download entire albums from khinsider from the commandline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loganswartz/khdownload",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "click",
        "bs4",
        "requests",
        "tqdm",
    ],
    entry_points="""
        [console_scripts]
        khdownload=khdownload.cli:cli
    """,
)
