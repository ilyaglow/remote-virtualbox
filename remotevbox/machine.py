"""
This module contains two classes:
* IMachine class represents IMachine object
* IProgress class represents IProgress object
* INetworkAdapter class represents INetworkAdapter object
"""
from base64 import b64decode
from datetime import datetime
from time import mktime

import zeep.exceptions
import semver

from .exceptions import (
    MachineCloneError,
    MachineCoredumpError,
    MachineCreateError,
    MachineDisableNetTraceError,
    MachineDiscardError,
    MachineEnableNetTraceError,
    MachineExtraDataError,
    MachineInfoError,
    MachineLaunchError,
    MachineLockError,
    MachinePauseError,
    MachinePowerdownError,
    MachineSaveError,
    MachineSetTraceFileError,
    MachineSnaphotError,
    MachineSnapshotError,
    MachineSnapshotNX,
    MachineUnlockError,
    MachineVrdeInfoError,
    ProgressTimeout,
    WrongLockState,
    WrongMachineState,
)


class IMachine(object):
    """IMachine constructs object with service, manager and id"""

    """Virtual machine states"""
    ABORTED = "Aborted"
    PAUSED = "Paused"
    POWEROFF = "PoweredOff"
    RUNNING = "Running"
    SAVED = "Saved"
    STUCK = "Stuck"

    """Session states"""
    LOCKED = "Locked"
    UNLOCKED = "Unlocked"

    """Launch modes"""
    HEADLESS = "headless"
    GUI = "gui"

    def __init__(self, service, manager, mid, vbox_version="6.1.0"):
        self.mid = mid
        self.service = service
        self.manager = manager
        self.session = self.manager.get_session(self.mid)
        self.console = None
        self.os = None
        self.mutable_id = None
        self.vbox_version = vbox_version

    def launch(self, mode="headless"):
        """Launches stopped or powered off machine
        Returns IProgress"""
        if self._get_state() == self.RUNNING:
            return

        try:
            if semver.compare(self.vbox_version, "6.1.0") == -1:
                progress = self.service.IMachine_launchVMProcess(
                    self.mid, self.session, mode, "",
                )
            else:
                progress = self.service.IMachine_launchVMProcess(
                    self.mid, self.session, mode,
                )
            iprogress = IProgress(progress, self.service)
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            raise MachineLaunchError("Launch operation failed: {}".format(err.message))

    def lock(self, mode="Shared"):
        """Locks current machine
        Could be Shared or Write
        If changing of the machine settings is needed then set mode to Write"""
        try:
            self.service.IMachine_lockMachine(self.mid, self.session, mode)
            self._get_mutable_id()
        except zeep.exceptions.Fault as err:
            raise MachineLockError("Lock operation failed: {}".format(err.message))

    def unlock(self):
        """Unlocks current machine"""
        try:
            self.service.ISession_unlockMachine(self.session)
        except zeep.exceptions.Fault as err:
            raise MachineUnlockError("Unlock operation failed: {}".format(err.message))

    def get_os(self):
        """Get Guest operating system type (user-defined value)"""
        self.os = self.service.IMachine_getOSTypeId(self.mid)
        return self.os

    def coredump(self, filepath, add_time_suffix=False):
        """Do ELF64 Core dump"""
        try:
            iconsole = self._get_console()

            if iconsole:
                imdebugger = self.service.IConsole_getDebugger(iconsole)

                if add_time_suffix:
                    filepath = "{}-{}".format(
                        filepath, int(mktime(datetime.now().timetuple()))
                    )

                self.service.IMachineDebugger_dumpGuestCore(imdebugger, filepath, "")
        except zeep.exceptions.Fault as err:
            raise MachineCoredumpError(
                "Coredump of guest's memory failed: {}".format(err.message)
            )

    def restore(self, snapshot_name=None):
        if self.state() == self.RUNNING:
            raise WrongMachineState("Can't restore a running machine")

        if snapshot_name is None:
            isnapshot = self._current_snapshot()
            if isnapshot is None:
                raise MachineSnapshotNX("Machine doesn't have a current snapshot")

        else:
            isnapshot = self._get_snapshot(snapshot_name)

        self.lock()

        iprogress = IProgress(
            self.service.IMachine_restoreSnapshot(self.mutable_id, isnapshot),
            self.service,
        )
        iprogress.wait()
        self.unlock()

    def discard(self, remove_state_file=True):
        """Discard Saved state to PoweredOff"""
        self.lock()
        try:
            self.service.IMachine_discardSavedState(self.mutable_id, remove_state_file)
            self.unlock()
        except zeep.exceptions.Fault as err:
            raise MachineDiscardError("Can't discard state: {}".format(err.message))

            self.unlock()

    def enable_net_trace(self, filename, slot=0):
        """Trace network adapter specified by a slot
        and dump pcap to specified filename
        Applicable only if state is PoweredOff"""

        if self._get_state() == self.POWEROFF or self._get_state() == self.SAVED:
            self.lock()
            adapter = INetworkAdapter(self.service, self.mutable_id, slot)
            adapter.enable_trace(filename)
            self.service.IMachine_saveSettings(self.mutable_id)
            self.unlock()
        else:
            raise WrongMachineState("Machine is not PoweredOff or Saved")

    def disable_net_trace(self, slot=0):
        if self._get_state() == self.POWEROFF:
            self.lock()
            adapter = INetworkAdapter(self.service, self.mutable_id, slot)
            adapter.disable_trace()
            self.service.IMachine_saveSettings(self.mutable_id)
            self.unlock()
        else:
            raise WrongMachineState("Machine state is not PoweredOff")

    def _current_snapshot(self):
        """Get ISnapshot object for current machine snapshot"""
        return self.service.IMachine_getCurrentSnapshot(self.mid)

    def _get_snapshot(self, name):
        """Return ISnapshot object by it's name"""
        try:
            return self.service.IMachine_findSnapshot(self.mid, name)

        except zeep.exceptions.Fault as err:
            if "Could not find a snapshost" in err:
                raise MachineSnapshotNX("Can't find snapshot {}".format(name))

            else:
                raise MachineSnapshotError(err)

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
        """Returns id with IConsole object"""
        if self._get_session_state() == self.LOCKED:
            return self.service.ISession_getConsole(self.session)

        else:
            raise WrongLockState("Session is not locked")

    def _get_mutable_id(self):
        """Return mutable ISession"""
        self.mutable_id = self.service.ISession_getMachine(self.session)

    def save(self):
        """Save state of running machine"""
        if self._get_session_state() == self.UNLOCKED:
            self.lock()

        try:
            self._get_mutable_id()
            iprogress = IProgress(
                self.service.IMachine_saveState(self.mutable_id), self.service
            )
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            raise MachineSaveError("Save operation failed: {}".format(err.message))

        if self._get_machine_session_state() == self.LOCKED:
            self.unlock()

    def state(self):
        """Returns machine current state"""
        return self._get_state()

    def save_and_discard(self):
        """Save virtual machine and discard the current state after"""
        state = self._get_state()

        if state == self.POWEROFF:
            raise WrongMachineState("Already powered off")

            return

        if state == self.RUNNING:
            self.save()

        if self._get_state() == self.SAVED:
            self.discard()

    def poweroff(self):
        """Power down virtual machine"""
        if self.state() not in [self.RUNNING, self.PAUSED, self.STUCK]:
            raise WrongMachineState(
                "Can't power down machine in {} state".format(self.state())
            )

        if self._get_session_state() == self.UNLOCKED:
            self.lock()

        try:
            iconsole = self._get_console()
            iprogress = IProgress(
                self.service.IConsole_powerDown(iconsole), self.service
            )
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            raise MachinePowerdownError(
                "Power down operation failed: {}".format(err.message)
            )

        if (
            self._get_machine_session_state() == self.LOCKED
            and self._get_session_state() == self.LOCKED
        ):
            self.unlock()

    def pause(self):
        """Set machine to pause state"""
        try:
            console = self._get_console()
            self.service.IConsole_pause(console)
        except zeep.exceptions.Fault as err:
            raise MachinePauseError("Pause operation failed: {}".format(err.message))

    def _get_extradata_keys(self):
        """Returns extradata keys"""
        try:
            keys = self.service.IMachine_getExtraDataKeys(self.mid)
        except zeep.exceptions.Fault as err:
            raise MachineExtraDataError(
                "ExtraDataKeys operation failed: {}".format(err.message)
            )

        return keys

    def extradata(self, key=None):
        """Get a specific value or all extradata on this machine.
           If key = None, returns a dictionnary containing all keys and values.
           else, return the requested data.
        """
        if not key:
            res = dict()
            for k in self._get_extradata_keys():
                res[k] = self.extradata(k)
            return res

        try:
            return_value = self.service.IMachine_getExtraData(self.mid, key)
        except zeep.exceptions.Fault as err:
            raise MachineExtraDataError(
                "Extradata operation failed: {}".format(err.message)
            )

        return return_value

    def set_extradata(self, key, value):
        """Sets extradata key to value on current machine.
        """
        if self._get_session_state() == self.UNLOCKED:
            self.lock()

        try:
            m2 = self.service.ISession_getMachine(self.session)
            self.service.IMachine_setExtraData(m2, key, value)
        except zeep.exceptions.Fault as err:
            raise MachineExtraDataError(
                "Extradata operation failed: {}".format(err.message)
            )

        if self._get_machine_session_state() == self.LOCKED:
            self.unlock()

    def info(self, key):
        # TODO : list of fetchable info
        progress = None
        try:
            progress = self.service.__getattr__("IMachine_get" + key)(self.mid)
        except zeep.exceptions.Fault as err:
            raise MachineInfoError(
                "Info error happened while trying to get key: {}. Message was: {}".format(
                    key, err.message
                )
            )

        return progress

    def vrde_info(self):
        """ Returns information about VRDE server."""
        info = dict()
        try:
            # Get VRDE Server:
            server = self.service.IMachine_getVRDEServer(self.mid)
            properties = self.service.IVRDEServer_getVRDEProperties(server)
            for property_name in properties:
                value = self.service.IVRDEServer_getVRDEProperty(server, property_name)
                info[property_name] = value
        except zeep.exceptions.Fault as err:
            raise MachineVrdeInfoError(
                "Failed to return information about VRDE server: {}".format(err.message)
            )

        return info

    def take_snapshot(self, target_name, target_description=""):
        """ Takes a snapshot of the current machine, named after target_name, with target_description as description."""
        if self._get_session_state() == self.UNLOCKED:
            self.lock()

        try:
            # session = self.manager.get_session(self.manager.handle)
            m2 = self.service.ISession_getMachine(self.session)
            result = self.service.IMachine_takeSnapshot(
                m2, target_name, target_description, False
            )

        except zeep.exceptions.Fault as err:
            raise MachineSnaphotError("Unable to take snapshot: {}".format(err.message))

        if self._get_machine_session_state() == self.LOCKED:
            self.unlock()
        return result

    def linked_clone(
        self, target_name, snapshot_name, mode="MachineState", options=["Link"]
    ):
        """ Creates a linked clone of a machine (needs a snapshot in order to work...) """
        try:
            mm = self.service.IVirtualBox_createMachine(
                self.manager.handle, "", target_name, "", "", ""
            )
        except zeep.exceptions.Fault as err:
            raise MachineCreateError("Unable to create machine: {}".format(err.message))

        try:
            snap = self._get_snapshot(snapshot_name)
            snap_machine_id = self.service.ISnapshot_getMachine(snap)

            clone = self.service.IMachine_cloneTo(snap_machine_id, mm, mode, options)

            iprogress = IProgress(clone, self.service)
            iprogress.wait()
        except zeep.exceptions.Fault as err:
            raise MachineCloneError("Unable to clone machine: {}".format(err.message))

        self.manager.service.IVirtualBox_registerMachine(self.manager.handle, mm)

    def get_screen_resolution(self, screen_number=0):
        iconsole = self._get_console()
        display = self.service.IConsole_getDisplay(iconsole)
        return self.service.IDisplay_getScreenResolution(display, screen_number)

    def take_screenshot_to_bytes(self, screen_number=0, image_format="PNG"):
        """Return the screenshot as an image.
        The image size is 1:1 with the screen size, by default is PNG.
        """
        iconsole = self._get_console()
        display = self.service.IConsole_getDisplay(iconsole)
        resolution = self.get_screen_resolution(screen_number)
        image_data = self.service.IDisplay_takeScreenShotToArray(
            display,
            screen_number,
            resolution["width"],
            resolution["height"],
            image_format,
        )
        return b64decode(image_data)

    def send_ctrl_alt_del(self):
        """Send Ctrl + Alt + Del to the machine."""
        iconsole = self._get_console()
        keyboard = self.service.IConsole_getKeyboard(iconsole)
        self.service.IKeyboard_putCAD(keyboard)

    def put_scancodes(self, scancodes):
        """Send a list of keyboard scancodes to the machine.

        The mapping between scancodes and character depends on the layout
        and the OS.

        For most cases the USB HID interface is easier to use.
        """
        iconsole = self._get_console()
        keyboard = self.service.IConsole_getKeyboard(iconsole)
        self.service.IKeyboard_putScancodes(keyboard, scancodes)

    def put_usagecode(self, code, page, release=False):
        """Send a USB HID usage code.

        When referring to keyboard, this signals that a key is being
        pressed. Use release=True to mark the end of the key press.

        Refer to the USB documentation for the codes, since this API has a
        very wide scope.
        """
        iconsole = self._get_console()
        keyboard = self.service.IConsole_getKeyboard(iconsole)
        self.service.IKeyboard_putUsageCode(keyboard, code, page, release)

    def release_keys(self):
        """Release every key currently considered pressed.

        Useful if the keyboard is out of sync, for example if the service was
        disconnected while a keystroke was being sent or some other keystroke
        was sent from another keyboard.
        """
        iconsole = self._get_console()
        keyboard = self.service.IConsole_getKeyboard(iconsole)
        self.service.IKeyboard_releaseKeys(keyboard)

    def put_mouse_event(
        self,
        dx,
        dy,
        dz=0,
        dw=0,
        left_pressed=False,
        right_pressed=False,
        middle_pressed=False,
    ):
        """Send a mouse event using relative coordinates.

        It consists of a relative movement, wheel movements and a key states.

        Position and wheel values can be negative and are in pixels.

        Parameters
        ----------
        dx : int
            movement to the right in pixels
        dy : int
            downward movement in pixels
        dz : int, optional
            clockwise wheel rotations, by default 0
        dw : int, optional
            horizontal wheel movement to the left, by default 0
        left_pressed : bool, optional
            whether the left button is pressed, by default False
        right_pressed : bool, optional
            whether the right button is pressed, by default False
        middle_pressed : bool, optional
            whether the middle button is pressed, by default False
        """
        button_state = (
            (0x01 * left_pressed) + (0x02 * right_pressed) + (0x03 * middle_pressed)
        )

        iconsole = self._get_console()
        mouse = self.service.IConsole_getMouse(iconsole)
        self.service.IMouse_putMouseEvent(mouse, dx, dy, dz, dw, button_state)

    def put_mouse_event_absolute(
        self,
        x,
        y,
        dz=0,
        dw=0,
        left_pressed=False,
        right_pressed=False,
        middle_pressed=False,
    ):
        """Send a mouse event using absolute coordinates.
        Not all guest hosts support it, use absolute_mouse_pointer_supported()
        to detect if this capability is available.

        It consists of an absolute position, wheel movements and a key states.
        Wheel values have the same meaning as the relative movement ones.

        Position and wheel values can be negative and are in pixels.

        Parameters
        ----------
        x : int
            position from the left border in pixels
        y : int
            position from the top border in pixels
        z : int, optional
            clockwise wheel rotations, by default 0
        w : int, optional
            horizontal wheel movement to the left, by default 0
        left_pressed : bool, optional
            whether the left button is pressed, by default False
        right_pressed : bool, optional
            whether the right button is pressed, by default False
        middle_pressed : bool, optional
            whether the middle button is pressed, by default False
        """
        button_state = (
            (0x01 * left_pressed) + (0x02 * right_pressed) + (0x03 * middle_pressed)
        )

        iconsole = self._get_console()
        mouse = self.service.IConsole_getMouse(iconsole)
        self.service.IMouse_putMouseEventAbsolute(mouse, x, y, dz, dw, button_state)

    def absolute_mouse_pointer_supported(self):
        """Return whether the guest OS supports absolute pointer positioning."""
        iconsole = self._get_console()
        mouse = self.service.IConsole_getMouse(iconsole)
        return self.service.IMouse_getAbsoluteSupported(mouse)


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
            raise ProgressTimeout("Progress wait failed: {}".format(err.message))

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
        return self.service.IMachine_getNetworkAdapter(self.machine, self.slot)

    def trace_enabled(self):
        return self.service.INetworkAdapter_getTraceEnabled(self.adapter)

    def enable_trace(self, filename):
        try:
            self.service.INetworkAdapter_setTraceEnabled(self.adapter, True)
        except zeep.exceptions.Fault as err:
            raise MachineEnableNetTraceError(
                "Failed to enable net trace: {}".format(err.message)
            )

        try:
            self.service.INetworkAdapter_setTraceFile(self.adapter, filename)
        except zeep.exceptions.Fault as err:
            raise MachineSetTraceFileError(
                "Failed to set pcap trace file: {}".format(err.message)
            )

    def disable_trace(self):
        try:
            self.service.INetworkAdapter_setTraceEnabled(self.adapter, False)
        except zeep.exceptions.Fault as err:
            raise MachineDisableNetTraceError(
                "Failed to disable net trace: {}".format(err.message)
            )
