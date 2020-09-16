import requests
import m3u8
import time
from datetime import datetime
import sys
import os


subject = sys.argv[1]
print(subject)
url_origin = "https://live.uia.no/live/"
url_identifier = "ngrp:"+subject+"_all/"
url_playlist = "/playlist.m3u8?DVR"

url_total = url_origin + url_identifier + url_playlist

outputFolder = "files/output/"
fileName = datetime.now().strftime("%Y_%m_%d_%H_%M_") + subject


def get_m3u8(uri):
    # TODO Errorhandeling if internet is lost
    er = False
    suc = False
    total_er = 0
    while (er == False and suc == False):
        try:
            req = requests.get(url_origin + url_identifier + uri)
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
    if(len(m.data["segments"]) <= 0 and len(m.data["playlists"]) <= 0 and er == True):
        return
    return m.data


def checkOutputFolder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


checkOutputFolder(outputFolder+subject)
currentMediaSequence = 0
active_Stream = True
# TODO Errorhandeling if internet is lost
# r = requests.get(url_total)
# m3u8_master = m3u8.loads(r.text)
m3u8_master = get_m3u8(url_playlist)
if (len(m3u8_master["playlists"]) > 0):
    p_uri = m3u8_master["playlists"][0]["uri"]
    lastValue = 0
    with open(outputFolder+subject+"/"+fileName+".ts", "wb") as f:
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
