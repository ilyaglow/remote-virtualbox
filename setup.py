"""
Setup script for remote-virtualbox library
"""

from setuptools import setup

setup(
    name='remotevbox',
    version='0.1.1',
    author='Ilya Glotov',
    author_email='ilya@ilyaglotov.com',
    packages=['remotevbox'],
    url='https://github.com/ilyaglow/remote-virtualbox',
    license='LICENSE',
    description='Simple client library to work with VirtualBox remotely',
    long_description=open('README.md').read(),
    install_requires=["zeep >= 2.4.0"],
    keywords='virtualbox soap remote',
    python_requires='>=2.7',
)
