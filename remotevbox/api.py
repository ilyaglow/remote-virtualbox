"""
Main API module
"""

from .vbox import IVirtualBox


def connect(location, user="", password=""):
    """Connects and returns IVirtualBox object"""
    return IVirtualBox(location, user, password)
