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
subjects = ["ing101", "mas134", "ma178", "ma209",
            "dat101", "dat233", "no008", "fys129", "ar", "selvkjor1-grm", "bio112", "byg227"]
url_origin = "https://live.uia.no/live/"
url_playlist = "/playlist.m3u8?DVR"

p = processHandeler.ProcessHandeler()
p.purgePidFile()
path = sys.path[0]
processes = []
for subject in subjects:
    m = record.m3u8_receiver()
    playlist = m.get_m3u8(url_origin + "ngrp:"+subject +
                          "_all/" + url_playlist,subject, False)
    if playlist:
        if(p.isRecording(subject)):
            print(subject + " is online, but it is already beeing recorded")

        else:
            print(subject + " is online, adding it to the que" )
            recorder = record.Record(subject)
            processes.append(Process(target=recorder.startRecording))

    else:
        print(subject + " is offline")
    time.sleep(1)


for process in processes:
    process.start()

for process in processes:
    process.join()
