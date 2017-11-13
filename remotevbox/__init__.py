"""
Remote VirtualBox library
-------------------------

Modern little package to do simple things with VirtualBox remotely

Usage:
    >>> import remotevbox
    >>> client = remotevbox.connect("http://127.0.0.1:18083", "vbox", "yourpassphrase")
    >>> client.get_version()
    '5.1.30'
"""

from  . import connect, disconnect
