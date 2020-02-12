"""
Setup script for remote-virtualbox library
"""

from setuptools import setup

setup(
    name="remotevbox",
    version="1.0.0",
    author="Ilya Glotov",
    author_email="ilya@ilyaglotov.com",
    packages=["remotevbox"],
    url="https://github.com/ilyaglow/remote-virtualbox",
    license="LICENSE",
    description="Simple client library to work with VirtualBox remotely",
    long_description=open("README.rst").read(),
    install_requires=["zeep >= 2.4.0", "semver >= 2.9.0"],
    keywords="virtualbox soap remote",
    python_requires=">=3.6",
)
