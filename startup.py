import requests
import m3u8
import time
import os
import sys
import json
import platform
import errno
import record
import processHandeler
from multiprocessing import Process
if platform.system() == "Windows":
    import psutil
subjects = ["ing101", "mas134", "ma178", "ma209",
            "dat101", "dat233", "no008", "fys129", "ar"]
url_origin = "https://live.uia.no/live/"
url_playlist = "/playlist.m3u8?DVR"

p = processHandeler.ProcessHandeler()
p.purgePidFile()
path = sys.path[0]
processes = []
for subject in subjects:
    m = record.m3u8_receiver()
    playlist = m.get_m3u8(url_origin + "ngrp:"+subject +
                          "_all/" + url_playlist, False)
    if playlist:
        print(subject + " is online")
        if(p.isRecording(subject)):
            print(subject + " is already beeing recorded")

        else:
            print("Starting recording in " + subject)
            recorder = record.Record(subject)
            processes.append(Process(target=recorder.startRecording))

            # if(platform.system() == "Windows"):
            #     subprocess.Popen(path + "/run.bat " + subject)
            # else:
            #     subprocess.Popen(path + "/run.sh " + subject)

    else:
        print(subject + " is offline")
        # recorder = record.Record(subject)
        # p = Process(target=recorder.startRecording)
        # processes.append(p)
    time.sleep(1)


for process in processes:
    process.start()

for process in processes:
    process.join()
