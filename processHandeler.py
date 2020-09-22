import platform
import errno
import os
import json
import platform
from time import time
if(platform.system() == "Windows"):
    import psutil

class ProcessHandeler:
    def __init__(self):
        self.pid = os.getpid()

    def processRunning(self, pid):
        if(platform.system() == "Linux"):
            if pid < 0:
                return False
            if pid == 0:
                # According to "man 2 kill" PID 0 refers to every process
                # in the process group of the calling process.
                # On certain systems 0 is a valid PID but we have no way
                # to know that in a portable fashion.
                raise ValueError('invalid PID 0')
            try:
                os.kill(pid, 0)
            except OSError as err:
                if err.errno == errno.ESRCH:
                    # ESRCH == No such process
                    return False
                elif err.errno == errno.EPERM:
                    # EPERM clearly means there's a process to deny access to
                    return True
                else:
                    # According to "man 2 kill" possible error values are
                    # (EINVAL, EPERM, ESRCH)
                    raise
            else:
                return True
        elif platform.system() == "Windows":
            return psutil.pid_exists(int(pid))

    def getPidFile(self):
        if os.path.exists("pid.json"):
            with open("pid.json") as json_data_file:
                return json.load(json_data_file)
        else:
            return {}

    def setPidFile(self, subject):
        jsonPidFile = self.getPidFile()
        pid = os.getpid()
        if not hasattr(jsonPidFile, str(pid)):
            pidSession = {}
            pidSession["subject"] = subject
            pidSession["timestamp"] = int(time())
            pidSession["pid"] = pid
            jsonPidFile[pid] = pidSession
            with open("pid.json", "w") as outputfile:
                json.dump(jsonPidFile, outputfile)

    # TODO delete PID when exiting program.

    def purgePidFile(self):
        pidFile = self.getPidFile()
        pidOut = {}
        for pidObj in pidFile:
            if self.processRunning(int(pidObj)):
                pidOut[pidObj] = pidFile[pidObj]

        with open("pid.json", "w") as pidFileOut:
            json.dump(pidOut, pidFileOut)

    def isRecording(self, subject):
        pidFile = self.getPidFile()
        for pid in pidFile:
            if (pidFile[pid]["subject"] == subject):
                return True

            else:
                return False
