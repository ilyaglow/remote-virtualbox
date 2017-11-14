"""
IMachine class represents IMachine object
"""

import logging
import zeep.exceptions


class IMachine(object):
    """IMachine constructs object with service, manager and id"""
    def __init__(self, service, manager, mid):
        self.mid = mid
        self.service = service
        self.manager = manager
        self.session = self.manager.get_session(self.mid)

    def launch(self):
        """Launches stopped or powered off machine
        Returns IProgress"""
        try:
            progress = self.service.IMachine_launchVMProcess(self.mid,
                                                             self.session,
                                                             "headless",
                                                             "")
            return progress
        except zeep.exceptions.Fault as err:
            logging.error(err)

    def stop(self):
        """Save state of running machine"""
        try:
            progress = self.service.IMachine_saveState(self.mid)
            return progress
        except zeep.exceptions.Fault as err:
            logging.error(err)
