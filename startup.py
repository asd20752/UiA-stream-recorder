import requests
import m3u8
import time
import os
subjects = ["ing101", "mas134", "ma178", "fys129"]
url_origin = "https://live.uia.no/live/"
url_playlist = "/playlist.m3u8?DVR"


def get_m3u8(uri, subject):

    # TODO Errorhandeling if internet is lost
    er = False
    suc = False
    total_er = 0
    while (er == False and suc == False):
        try:
            req = requests.get(url_origin + "ngrp:"+subject+"_all/" + uri)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("m3u8 failed, not able to connect to the server")
            er = True
        except requests.exceptions.HTTPError:
            print("m3u8, HTTP error 4xx 5xx")
            er = True

        if(er == False):
            m = m3u8.loads(req.text)
            suc = True
            # print("Fetching m3u8")
            # print("Segments: " + str(len(m.data["segments"])) +
            #   ", Playlists: " + str(len(m.data["playlists"])))

        else:
            total_er += 1
            if(total_er < 10):
                er = False
                time.sleep(2)
            else:
                er = True
                return
    if(len(m.data["segments"]) <= 0 and len(m.data["playlists"]) <= 0):
        return
    return m.data


for subject in subjects:
    playlist = get_m3u8(url_playlist, subject)
    if playlist:
        print(subject + " is online")
        os.system("python main.py " + subject)
    else:
        print(subject + " is offline")
