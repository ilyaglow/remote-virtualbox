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
        self.console = None
        self.os = None
        self.mutable_id = None

    def launch(self):
        """Launches stopped or powered off machine
        Returns IProgress"""
        try:
            progress = self.service.IMachine_launchVMProcess(self.mid,
                                                             self.session,
                                                             "headless",
                                                             "")
            iprogress = IProgress(progress, self.service)
            iprogress.wait()
            self.console = self._get_console()
        except zeep.exceptions.Fault as err:
            logging.error("Launch operation failed: %s", err)

    def lock(self, mode="Shared"):
        """Locks current machine could be Shared or Write
        If changing of the machine settings is needed then set mode to Write"""
        try:
            self.service.IMachine_lockMachine(self.mid,
                                              self.session,
                                              mode)
        except zeep.exceptions.Fault as err:
            logging.error("Lock operation failed: %s", err)

    def unlock(self):
        """Unlocks current machine"""
        try:
            self.service.ISession_unlockMachine(self.session)
        except zeep.exceptions.Fault as err:
            logging.error("Unlock operation failed: %s", err)

    def get_os(self):
        """Get Guest operating system type (user-defined value)"""
        self.os = self.service.IMachine_getOSTypeId(self.mid)
        return self.os

    def _get_session_state(self):
        """Get state of the current session"""
        return self.service.ISession_getState(self.session)

    def _get_state(self):
        """Get state of machine"""
        return self.service.IMachine_getState(self.mid)

    def _get_console(self):
        """Returns id with IConsole obect"""
        return self.service.ISession_getConsole(self.session)

    def _get_mutable_id(self):
        """Return mutable ISession"""
        self.mutable_id = self.service.ISession_getMachine(self.session)

    def save(self):
        """Save state of running machine"""
        try:
            self._get_mutable_id()
            iprogress = IProgress(self.service.IMachine_saveState(self.mutable_id),
                                  self.service)
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            logging.error("Save operation failed: %s", err)

    def pause(self):
        """Set machine to pause state"""
        self.service.IConsole_pause(self.console)


class IProgress(object):
    """IProgress constructs object to deal with waiting"""
    def __init__(self, progress_id, service):
        self.pid = progress_id
        self.service = service

    def wait(self, miliseconds=-1):
        """Wait for infinite time by default"""
        try:
            self.service.IProgress_waitForCompletion(self.pid, miliseconds)
        except zeep.exceptions.Fault as err:
            logging.error("Progress wait failed: %s", err)

        return self.status()

    def status(self):
        """Check status of the progress"""
        status = self.service.IProgress_getResultCode(self.pid)
        if status != 0:
            return "Fail"

        return "Success"
