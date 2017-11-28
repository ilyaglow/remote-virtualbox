"""
This module contains two classes:
* IMachine class represents IMachine object
* IProgress class represents IProgress object
"""

from datetime import datetime
from time import mktime
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

    def launch(self, mode="headless"):
        """Launches stopped or powered off machine
        Returns IProgress"""
        try:
            progress = self.service.IMachine_launchVMProcess(self.mid,
                                                             self.session,
                                                             mode,
                                                             "")
            iprogress = IProgress(progress, self.service)
            iprogress.wait()
            self.console = self._get_console()
        except zeep.exceptions.Fault as err:
            logging.error("Launch operation failed: %s", err)

    def lock(self, mode="Shared"):
        """Locks current machine
        Could be Shared or Write
        If changing of the machine settings is needed then set mode to Write"""
        try:
            self.service.IMachine_lockMachine(self.mid,
                                              self.session,
                                              mode)
            self._get_mutable_id()
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

    def coredump(self, filepath, add_time_suffix=False):
        """Do ELF64 Core dump"""
        iconsole = self._get_console()

        if iconsole:
            imdebugger = self.service.IConsole_getDebugger(iconsole)

            if add_time_suffix:
                filepath = "{}-{}".format(filepath,
                                          int(mktime(datetime.now().timetuple())))

            self.service.IMachineDebugger_dumpGuestCore(imdebugger,
                                                        filepath,
                                                        '')

    def restore(self, snapshot_name=None):
        if snapshot_name is None:
            isnapshot = self._current_snapshot()
        else:
            isnapshot = self._get_snapshot(snapshot_name)

        self.lock()

        iprogress = IProgress(self.service.IMachine_restoreSnapshot(self.mutable_id, isnapshot),
                              self.service)
        iprogress.wait()
        self.unlock()

    def discard(self, remove_state_file=True):
        """Discard Saved state to PoweredOff"""
        self.lock()
        try:
            self.service.IMachine_discardSavedState(self.mutable_id,
                                                    remove_state_file)
            self.unlock()
        except zeep.exceptions.Fault as err:
            logging.error("Can't discard state: %s", err)
            self.unlock()

    def enable_net_trace(self, filename, slot=0):
        """Trace network adapter specified by a slot
        and dump pcap to specified filename
        Applicable only if state is PoweredOff"""

        if self._get_state() == "PoweredOff":
            self.lock()
            adapter = INetworkAdapter(self.service, self.mutable_id, slot)
            adapter.enable_trace(filename)
            self.service.IMachine_saveSettings(self.mutable_id)
            self.unlock()
        else:
            logging.error("Machine state is not PoweredOff")

    def disable_net_trace(self, slot=0):
        if self._get_state() == "PoweredOff":
            self.lock()
            adapter = INetworkAdapter(self.service, self.mutable_id, slot)
            adapter.disable_trace()
            self.service.IMachine_saveSettings(self.mutable_id)
            self.unlock()
        else:
            logging.error("Machine state is not PoweredOff")

    def _current_snapshot(self):
        """Get ISnapshot object for current machine snapshot"""
        return self.service.IMachine_getCurrentSnapshot(self.mid)

    def _get_snapshot(self, name):
        """Return ISnapshot object by it's name"""
        try:
            return self.service.IMachine_findSnapshot(self.mid, name)
        except zeep.exceptions.Fault as err:
            if 'Could not find a snapshost' in err:
                logging.error("Can't find snapshot %s", name)
            else:
                logging.error(err)

    def _snapshot_count(self):
        """Returns count of machine snapshots"""
        return self.service.IMachine_getSnapshotCount(self.mid)

    def _get_session_state(self):
        """Get state of the current session"""
        return self.service.ISession_getState(self.session)

    def _get_machine_session_state(self):
        """Get state of the current machine session"""
        return self.service.IMachine_getSessionState(self.mid)

    def _get_state(self):
        """Get execution state of a machine"""
        return self.service.IMachine_getState(self.mid)

    def _get_console(self):
        """Returns id with IConsole obect"""
        if self._get_session_state() == 'Locked':
            return self.service.ISession_getConsole(self.session)
        else:
            logging.error("Session is not locked")

    def _get_mutable_id(self):
        """Return mutable ISession"""
        self.mutable_id = self.service.ISession_getMachine(self.session)

    def save(self):
        """Save state of running machine"""
        locked = False

        if self._get_session_state() == "Unlocked":
            self.lock()
            locked = True

        try:
            self._get_mutable_id()
            iprogress = IProgress(self.service.IMachine_saveState(self.mutable_id),
                                  self.service)
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            logging.error("Save operation failed: %s", err)

        if locked:
            self.unlock()

    def state(self):
        """Returns machine current state"""
        return self._get_state()

    def poweroff(self):
        """Save virtual machine and poweroff it after"""
        state = self._get_state()

        if state == "PoweredOff":
            logging.error("Already powered off")
            return

        if state == "Running":
            self.save()

        if self._get_state() == "Saved":
            self.discard()

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


class INetworkAdapter(object):
    """INetworkAdapter works with selected machine's network adapter"""
    def __init__(self, service, machine_id, slot=0):
        self.machine = machine_id
        self.service = service
        self.slot = slot
        self.adapter = self._get_adapter()

    def _get_adapter(self):
        return self.service.IMachine_getNetworkAdapter(self.machine,
                                                       self.slot)

    def trace_enabled(self):
        return self.service.INetworkAdapter_getTraceEnabled(self.adapter)

    def enable_trace(self, filename):
        self.service.INetworkAdapter_setTraceEnabled(self.adapter, True)
        self.service.INetworkAdapter_setTraceFile(self.adapter, filename)

    def disable_trace(self):
        self.service.INetworkAdapter_setTraceEnabled(self.adapter, False)
