"""
IVirtualBox binding
"""

import logging
import requests.exceptions
import sys
import zeep

from .machine import IMachine
from .websession_manager import IWebsessionManager

VBOX_SOAP_BINDING = '{http://www.virtualbox.org/}vboxBinding'


class IVirtualBox(object):
    def __init__(self, location, user, password):
        self.log = logging.getLogger()

        if not location.endswith('/'):
            location = location + '/'

        self.location = location
        self.client = self.get_client(location + '?wsdl')
        self.service = self.client.create_service(VBOX_SOAP_BINDING,
                                                  self.location)
        self.manager = IWebsessionManager(self.service, user, password)

        self.handle = self.manager.handle

    def get_client(self, location):
        try:
            client = zeep.Client(location)
            return client
        except requests.exceptions.ConnectionError:
            logging.error("Location: {} is not available".format(location))
            sys.exit(1)

    def get_session_manager(self):
        return self.manager

    def list_machines(self):
        """Lists all machines available"""
        machines = []
        for machine in self.service.IVirtualBox_getMachines(self.handle):
            try:
                machines.append(self.service.IMachine_getName(machine))
            except zeep.exceptions.Fault as err:
                if 'The object functionality is limited' in str(err):
                    """This error means that something is wrong with iterated machine
                    medium or settings.
                    Simply ignore this VM"""
                    pass
                else:
                    logging.error(err)

        return machines

    def get_machine(self, name):
        """Returns IMachine"""
        mid = self.find_machine(name)
        return IMachine(self.service, self.manager, mid)

    def find_machine(self, name):
        """Returns virtual machine identificator by it's name"""
        try:
            return self.service.IVirtualBox_findMachine(self.handle, name)
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

    def get_version(self):
        """Returns string with a VirtualBox version"""
        return self.service.IVirtualBox_getVersion(self.handle)

    def disconnect(self):
        """Disconnects"""
        self.manager.logoff()
