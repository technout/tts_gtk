# TTS_GTK
Graphical interface for Coqui TTS (Text to Speech) command line. Made in GTK3 and Python3 for the Linux platform.

This program uses the [Coqui TTS](https://github.com/coqui-ai/TTS) software for converting text to speech. Coqui TTS is a deep learning based text-to-speech solution. This is a very interesting project and is constantly updated and improving fast. You can use it from command line or install it as a server. I decided to add a third option: A GTK3 graphical interface. I also added multithreading support and use all the cpu cores you have. While audio is playing, the next lines of text will be processed in the background. I started this project so i can copy and paste some text from the web and let the computer read it to me, after a while this first beta version came to life. But still a work in progress, you can add to the project as well, all help is welcome. And help to improve this faster!

Queuing technique
-----------------
With TTS there was a word limit, with TTS_GTK you can add very long texts. If all CPU cores are busy or not enough RAM is available, the next lines will be queued until there is RAM and cores available again to process them. This makes it possible to read out long web pages almost realtime with a simple copy and paste command.

Language support: English, German, Spanish, French, Italian and some other languages have voice models (See Coqui TTS)

TTS_GTK is not for training models, it can only use pre-trained models.

The sentence read out as audio is visible as the blue text:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_1.png)

You can also change some parameters (like the audio speed or the voice model) with extra options, some examples:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_3.png)

Requirements
------------
For running TTS or TTS_GTK it is advisable to have a modern cpu, 4-core cpu with 8GB of RAM will do the job.

Installation
------------
TTS and TTS_GTK is working with Ubuntu 18.04 (or newer) with python >= 3.7, < 3.11..

1) If you don't have Python3 installed, start with that: <br />
```sudo apt install python3```

2) Then install TTS with: <br />
```pip install TTS``` <br />
(this will download approximately 1,1 GB including the English voicemodel)

3) TTS_GTK need some modules, you can install them with: <br />
```pip install pyrubberband pydub pygame psutil```

4) You also need espeak-ng for the voice model: <br /> ```sudo apt install espeak-ng```

5) Now download or git clone this TTS_GTK project (you just need two files: tts_gtk.py and tts_gtk.glade)

6) Place them in the same directory (where you have normal read and write access to)

7) Before running TTS_GTK please test if TTS is working, test it with a simple command line: <br />
```tts --text "Hello world." --model_name "tts_models/en/ljspeech/vits"``` (if no errors appear, it will work fine)

- Error: if TTS is not found, add the tts directory to your PATH variable: <br /> 
```export PATH="$PATH:/home/your_username/.local/bin"```
If that is working, you can add this line to your user profile, to make it permanent after a reboot: ```nano ~/.profile``` <br /> 
Or check with ```pip list``` if it is installed. <br /> 

8) Run it from command line: <br /> ```python3 /path/to/file/tts_gtk.py```)

TTS_GTK is working with Coqui TTS version 0.8. It can also work with older versions, but you need to add the --max_words=14 option in the Extra options text area. So the lines are cut in shorter sentences. I you don't do this you might end up with audio playback ending in the middle of a sentence.

Extra options text area
-----------------------
Extra options you can use:
```
--playspeed=0.9     Use to increase or decrease audio speed.
        Default is 1, 1.1 is 10% faster, 0.7 is 30% slower.
--crossfade=60      Crossfade is used to merge the audio lines
        together. Default is 60ms, you can increase or
        decrease this.
--voicemodel=tts_models/en/ljspeech/vits    This is the default
        voicemodel, you can use others like:
        tts_models/nl/mai/tacotron2-DDC
--max_words=14      Maximum words per line. The TTS processor
        has its limits (as for version 0.7.1).
        The default workable value now is 40 words.
        This can be changed in newer releases.
```
License
-------
TTS_GTK is released under the terms of the Mozilla Public License 2.0 (as well for TTS). Please refer to the LICENSE file.
