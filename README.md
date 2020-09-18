# UiA-stream-recorder

Python V3

Third party dependencies
* m3u8
* Requests
* psutil (Windows)
  
## 1.1 Setup
* Download the script or clone it from GitHub. Save it to a folder where it can be easily run with enough space for media files. 
* Change what cources to monitor in the setup.py file under the variable subjects. This should be the code displayd in the url of the web stream. The course names has to be lower case. 
* Install the dependencies listed above. 
* By default the linux script runs python3 command. If this errors try chaning the run.sh "python3" to "python" 

## 1.2 Running 
The script can be set up as a cronjob to check for new video streams. startup.py will check for new streams and if they are allready recording. If a recording of a subject is already underway it will not interfeer but check for other streams. 

## 1.3 Finnishing
When the stream is finnished it might be a good idea to transcode the recorded file to another more versitile format like mp4. This is a job easily done with FFMPEG. 

