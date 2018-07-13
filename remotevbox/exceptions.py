"""
Exceptions handling
"""

"""
Service related exceptions
"""


class WebServiceConnectionError(Exception):
    """VirtualBox Web Service is not available to connect"""


class ListMachinesError(Exception):
    """Failed to list machines"""


class FindMachineError(Exception):
    """Failed to find machine"""


class WrongCredentialsError(Exception):
    """Wrong credentials supplied"""


"""
Machine related exceptions
"""


class MachineLaunchError(Exception):
    """Failed to launch virtual machine"""


class MachineLockError(Exception):
    """Failed to lock virtual machine"""


class MachineUnlockError(Exception):
    """Failed to unlock virtual machine"""


class MachineDiscardError(Exception):
    """Failed to discard saved state of a virtual machine"""


class WrongMachineState(Exception):
    """Machine in a wrong state to do a task"""


class MachineSnapshotError(Exception):
    """Failed to get snapshot of a machine"""


class MachineSnapshotNX(Exception):
    """Machine snapshot doesn't exist"""


class WrongLockState(Exception):
    """Machine in a wrong state"""


class MachineSaveError(Exception):
    """Failed to save virtual machine"""


class MachinePowerdownError(Exception):
    """Failed to power down virtual machine"""


class MachineExtraDataError(Exception):
    """Error while fetching/Getting machine extradata"""


class MachineInfoError(Exception):
    """Error while getting/setting machine information"""


class MachineCloneError(Exception):
    """Error while cloning a machine"""


class MachineSnaphotError(Exception):
    """Error while snapshoting a machine"""


class MachineVrdeInfoError(Exception):
    """Error while fetching VRDE Server info"""


class ProgressTimeout(Exception):
    """Progress has been timed out"""


class MachineEnableNetTraceError(Exception):
    """Failed to enable machine network tracing"""


class MachineDisableNetTraceError(Exception):
    """Failed to disable machine network tracing"""


class MachineSetTraceFileError(Exception):
    """Failed to set a pcap trace file"""


class MachinePauseError(Exception):
    """Failed to pause machine"""


class MachineCoredumpError(Exception):
    """Failed to take machine core dump"""


class MachineCreateError(Exception):
    """Failed to create machine"""
