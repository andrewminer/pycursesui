"""Define the pycursesui package."""
# Taken from the following sample: https://github.com/pypa/sampleproject/blob/master/setup.py

import setuptools

setuptools.setup(
    name="pycursesui",
    version="0.0.1",
    description="A python UI framework for command-line applications using curses",
    author="Andrew Miner",
    author_email="andrewminer@mac.com",

    packages=[
        "pycurses",
    ],
    package_dir={"": "src"},

    install_requires=[
    ],
)
