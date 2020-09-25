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
  Download the script or clone it from GitHub. Save it to a folder where it can be easily run with enough space for media files. 


# 3. Automatic recording
## 3.1. Setup
Change what courses to monitor in the setup.py file under the variable subjects. This subject tag is the same as displayed in the URL of the web stream. The course names has to be lower case. 

## 3.2. Running 
The script can be set up as a cronjob to check for new video streams. startup.py will check for new streams and if they are allready recording. If a recording of a subject is already underway it will not interfeer but check for other streams. 

## 3.3. Finishing
All streams are recorded in a .ts file format, so when the stream is finished it might be a good idea to transcode the recorded file to a more versitile format like mp4. This is a job easily completed with programs like Handbrake or FFMPEG(Is know to throw errors)
    
# 4. Manual recording
Under construction
<!-- Is currently not working
To start a recording manualy. Run the command "python record.py [subject code]"  -->