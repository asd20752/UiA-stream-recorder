import requests
import m3u8
import time
from datetime import datetime
import sys
import os
import json
import platform
import errno
from processHandeler import ProcessHandeler
if(platform.system() == "Windows"):
    import psutil


class m3u8_receiver:

    def get_m3u8(self, url):
        # TODO Errorhandeling if internet is lost
        er = False
        suc = False
        total_er = 0
        while (er == False and suc == False):
            try:
                req = requests.get(url, timeout=5)
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


class Record:
    def __init__(self, subject):
        self.emne = subject
        self.active_Stream = True
        self.url_origin = "https://live.uia.no/live/"
        self.url_identifier = "ngrp:"+self.emne+"_all/"
        self.url_playlist = "/playlist.m3u8?DVR"
        self.url_total = self.url_origin + self.url_identifier + self.url_playlist
        self.outputFolder = "files/output/"
        self.fileName = datetime.now().strftime("%Y_%m_%d_%H_%M_") + self.emne
        self.currentMediaSequence = 0


    def init(self):
        handeler = ProcessHandeler()
        handeler.purgePidFile()
        self.checkOutputFolder(self.outputFolder+self.emne)
        self.active_Stream = True
        # m3u8_master = get_m3u8(url_playlist)
        handeler.setPidFile(self.emne)
        if(not self.emne):
            print(
                "No subject defined, add the wanted subject to record. Example: python record.py [subject]")
            exit()
            emne = sys.argv[1]
            print(emne)

    def checkOutputFolder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def startRecording(self):
        self.init()
        # emne = subject
        print("Starting recoring in: " + self.emne)
        i = 1
        while i <= 10:
            time.sleep(2)
            i += 1
        # record()

    def record(self):
        m = m3u8_receiver(self.url_total)
        m3u8_master = m.get_m3u8(self.url_total)
        if (not m3u8_master is None and len(m3u8_master["playlists"]) > 0):
            p_uri = m3u8_master["playlists"][0]["uri"]
            lastValue = 0
            with open(self.outputFolder+self.emne+"/"+self.fileName+".ts", "wb") as f:
                while (self.active_Stream):
                    seg = m3u8_receiver().get_m3u8(self.url_origin + self.url_identifier + p_uri)
                    if not seg:
                        print("The stream seems to be terminated")
                        exit()
                        self.active_Stream = False
                        break

                    else:
                        timing = 0
                        startTime = time.time()
                        if(self.currentMediaSequence == 0):
                            self.currentMediaSequence = seg["media_sequence"]
                            startIndex = 0
                        else:
                            startIndex = self.currentMediaSequence - \
                                seg["media_sequence"]
                            startIndex = startIndex if startIndex >= 0 else 0

                        i = 0
                        print(startIndex)
                        fatal_errors = 0
                        errors = 0
                        err = False
                        while (i < len(seg["segments"]) and fatal_errors < 10):
                            element = seg["segments"][i]
                            timing += element["duration"]
                            i += 1
                            if (i > startIndex):
                                print(element["uri"])
                                try:
                                    r = requests.get(
                                        self.url_origin + self.url_identifier + element["uri"], timeout=(5, 10))
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
                                    self.currentMediaSequence += 1
                                    errors = 0
                                else:
                                    if(errors < 10):
                                        i -= 1 if i > 0 else 0
                                        time.sleep(2)
                                    else:
                                        fatal_errors += 1
                            #To try to prevent getting caught by the anti bot detection
                            time.sleep(0.5)
                        elapsedTime = time.time() - startTime
                        sleepTime = (timing - elapsedTime) / 2

                        print("Elapsed time for this m3u8: " +
                              str(int(elapsedTime)) + "s sleeping for: " + str(int(sleepTime))+"s" + " Media Sequence: " + str(self.currentMediaSequence))
                        sleepTime = sleepTime if sleepTime >= 0 else 3
                        time.sleep(sleepTime)
        else:
            print("Did not find a video stream")
            exit()
