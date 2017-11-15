"""
IWebsession_Manager binding
"""

import logging
import zeep.exceptions


class IWebsessionManager(object):
    """
    IWebsessionManager retrieves handle and current session
    """
    def __init__(self, service, user, password):
        self.service = service
        self.handle = self.login(user, password)

        if self.handle:
            self.session = self.get_session(self.handle)

    def get_session(self, handle):
        """Retrieves current SessionObject"""
        return self.service.IWebsessionManager_getSessionObject(handle)

    def login(self, user, password):
        """Use IWebsessionManager to login and exit if credentials are false

        :param user: username (VBOX_USER from /etc/default/virtualbox)
        :param password: unix password of the supplied user on VirtualBox host
        """
        try:
            return self.service.IWebsessionManager_logon(user, password)
        except zeep.exceptions.Fault:
            logging.error("Wrong credentials supplied")

    def logoff(self):
        """Logs off and destroy all managed object references"""
        self.service.IWebsessionManager_logoff(self.handle)
