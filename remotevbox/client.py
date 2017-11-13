"""
IVirtualBox binding
"""

import logging
import zeep

from . import IMachine

VBOX_SOAP_BINDING = '{http://www.virtualbox.org/}vboxBinding'


class IVirtualBox():
    def __init__(self, location, user, password):
        self.log = logging.getLogger()

        if not location.endswith('/'):
            location = location + '/'

        self.location = location
        self.client = zeep.Client(location + '?wsdl')
        self.service = self.client.create_service(VBOX_SOAP_BINDING,
                                                  self.location)
        self.login(user, password)

    def login(self, user, password):
        """Use IWebsessionManager to login and exit if credentials are false

        :param user: username (VBOX_USER from /etc/default/virtualbox)
        :param password: unix password of the supplied user on VirtualBox host
        """
        try:
            self.handle = self.service.IWebsessionManager_logon(user, password)
        except zeep.exceptions.Fault:
            logging.error("Wrong credentials supplied")

    def get_machines(self):
        """Lists all machines available"""
        return self.service.IVirtualBox_getMachines(self.handle)

    def find_machine(self, name):
        """Returns virtual machine identificator by it's name"""
        try:
            id = self.service.IVirtualBox_findMachine(self.handle, name)
        except zeep.exceptions.Fault as e:
            logging.error(e)

    def open_machine(self, name):
        """Constructs :class:`IMachine <IMachine>`

        Will check if provided machine exists and return and object

        :param name: virtual machine name
        """

        # return IMachine(self.service.IVirtualBox_openMachine(self.handle, name),
        #                 self.handle)
        pass

    def start_machine(self, name):
        pass

    def stop_machine(self, name):
        pass

    def get_version(self):
        """Returns string with a VirtualBox version"""
        return self.service.IVirtualBox_getVersion(self.handle)
