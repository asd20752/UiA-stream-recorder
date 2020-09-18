# 1. UiA-stream-recorder

- [1. UiA-stream-recorder](#1-uia-stream-recorder)
- [2. Setup environment](#2-setup-environment)
  - [2.1. Requirements](#21-requirements)
  - [2.2. Setting up folders](#22-setting-up-folders)
- [3. Automatic recording](#3-automatic-recording)
  - [3.1. Setup](#31-setup)
  - [3.2. Running](#32-running)
  - [3.3. Finishing](#33-finishing)
- [4. Manual recording](#4-manual-recording)


# 2. Setup environment

## 2.1. Requirements
* Python V3
* [m3u8](https://pypi.org/project/m3u8/) 
* [Requests](https://pypi.org/project/requests/)
* [psutil](https://pypi.org/project/psutil/) (Windows)
  
## 2.2. Setting up folders
  * Download the script or clone it from GitHub. Save it to a folder where it can be easily run with enough space for media files. 


# 3. Automatic recording
## 3.1. Setup
* Change what cources to monitor in the setup.py file under the variable subjects. This should be the code displayd in the url of the web stream. The course names has to be lower case. 
* By default the linux script runs python3 command. If this errors try chaning the run.sh "python3" to "python" 

## 3.2. Running 
The script can be set up as a cronjob to check for new video streams. startup.py will check for new streams and if they are allready recording. If a recording of a subject is already underway it will not interfeer but check for other streams. 

## 3.3. Finishing
When the stream is finnished it might be a good idea to transcode the recorded file to another more versitile format like mp4. This is a job easily done with FFMPEG. 
    
# 4. Manual recording
To start a recording manualy. Run the command "python record.py [subject code]" 