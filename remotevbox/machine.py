"""
IMachine class represents IMachine object
"""


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
        progress = self.service.IMachine_launchVMProcess(self.mid,
                                                         self.session,
                                                         "nogui",
                                                         "")
        return progress

    def stop(self):
        """Save state of running machine"""
        progress = self.service.IMachine_saveState(self.mid)
        return progress
