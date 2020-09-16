import requests
import m3u8
import time
from datetime import datetime
import sys
import os
import json
import platform
import errno
if(platform.system() == "Windows"):
    import psutil

if(len(sys.argv) <= 1):
    print(
        "No subject defined, add the wanted subject to record. Example: python main.py [subject]")
    exit()
emne = sys.argv[1]
print(emne)
url_origin = "https://live.uia.no/live/"
url_identifier = "ngrp:"+emne+"_all/"
url_playlist = "/playlist.m3u8?DVR"

url_total = url_origin + url_identifier + url_playlist

outputFolder = "files/output/"
fileName = datetime.now().strftime("%Y_%m_%d_%H_%M_") + emne


def get_m3u8(uri):
    # TODO Errorhandeling if internet is lost
    er = False
    suc = False
    total_er = 0
    while (er == False and suc == False):
        try:
            req = requests.get(url_origin + url_identifier + uri)
            er = False
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("m3u8 failed, not able to connect to the server")
            er = True
        except requests.exceptions.HTTPError:
            print("m3u8, HTTP error 4xx 5xx")
            er = True

        if(er == False):
            m = m3u8.loads(req.text)
            suc = True
            print("Fetching m3u8")
            print("Segments: " + str(len(m.data["segments"])) +
                  ", Playlists: " + str(len(m.data["playlists"])))

        else:
            total_er += 1
            if(total_er < 10):
                er = False
                time.sleep(2)
            else:
                er = True
                return
    # TODO Check if er should be and or or
    if((len(m.data["segments"]) <= 0 and len(m.data["playlists"]) <= 0) or er == True):
        return
    return m.data


def checkOutputFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def processRunning(pid):
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


def getPidFile():
    if os.path.exists("pid.json"):
        with open("pid.json") as json_data_file:
            return json.load(json_data_file)
    else:
        return {}


def setPidFile():
    jsonPidFile = getPidFile()
    pid = os.getpid()
    if not hasattr(jsonPidFile, str(pid)):
        pidSession = {}
        pidSession["subject"] = emne
        pidSession["timestamp"] = int(time.time())
        pidSession["pid"] = pid
        jsonPidFile[pid] = pidSession
        with open("pid.json", "w") as outputfile:
            json.dump(jsonPidFile, outputfile)


def purgePidFile():
    pidFile = getPidFile()
    pidOut = {}
    for pidObj in pidFile:
        if processRunning(int(pidObj)):
            pidOut[pidObj] = pidFile[pidObj]

    with open("pid.json", "w") as pidFileOut:
        json.dump(pidOut, pidFileOut)


purgePidFile()
checkOutputFolder(outputFolder+emne)
currentMediaSequence = 0
active_Stream = True
# TODO Errorhandeling if internet is lost
# r = requests.get(url_total)
# m3u8_master = m3u8.loads(r.text)
m3u8_master = get_m3u8(url_playlist)
setPidFile()
if (hasattr(m3u8_master, "playlists") and len(m3u8_master["playlists"]) > 0):
    p_uri = m3u8_master["playlists"][0]["uri"]
    lastValue = 0
    with open(outputFolder+emne+"/"+fileName+".ts", "wb") as f:
        while (active_Stream):
            seg = get_m3u8(p_uri)
            if not seg:
                print("The stream seems to be terminated")
                active_Stream = False
                break

            else:
                timing = 0
                startTime = time.time()
                if(currentMediaSequence == 0):
                    currentMediaSequence = seg["media_sequence"]
                    startIndex = 0
                else:
                    startIndex = currentMediaSequence - seg["media_sequence"]
                    startIndex = startIndex if startIndex >= 0 else 0

                i = 0
                print(startIndex)
                # for element, index in seg["segments"]:
                fatal_errors = 0
                errors = 0
                err = False
                while (i < len(seg["segments"]) and fatal_errors < 10):
                    element = seg["segments"][i]
                    timing += element["duration"]
                    i += 1
                    if (i > startIndex):
                        print(element["uri"])
                        # TODO Errorhandeling if internet is lost
                        try:
                            r = requests.get(
                                url_origin + url_identifier + element["uri"])
                            err = False
                        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError):
                            print(
                                "Failed to connect to the server, trying again in 2 seconds")
                            errors += 1
                            err = True
                        except requests.exceptions.HTTPError:
                            print("HTTP error 4xx 5xx")
                            errors += 1
                            err = True

                        if(err == False):
                            f.write(r.content)
                            lastValue = lastValue + 1
                            currentMediaSequence += 1
                            errors = 0
                        else:
                            if(errors < 10):
                                i -= 1 if i > 0 else 0
                                time.sleep(2)
                            else:
                                fatal_errors += 1

                elapsedTime = time.time() - startTime
                sleepTime = (timing - elapsedTime) / 2

                print("Elapsed time for this m3u8: " +
                      str(int(elapsedTime)) + "s sleeping for: " + str(int(sleepTime))+"s" + " Media Sequence: " + str(currentMediaSequence))
                time.sleep(sleepTime)
else:
    print("Did not find a video stream")
    exit()
