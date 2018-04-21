"""
Remote VirtualBox library
-------------------------

Modern little package to do simple things with VirtualBox remotely

Usage:
    >>> import remotevbox
    >>> vbox = remotevbox.connect("http://127.0.0.1:18083", "vbox", "yourpassphrase")
    >>> vbox.get_version()
    '5.1.30'
    >>> machine = vbox.get_machine("Windows10")
    >>> machine.launch()
    >>> machine.save()
    >>> vbox.disconnect()
"""

from .api import connect
