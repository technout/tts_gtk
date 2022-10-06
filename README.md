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
For running TTS or TTS_GTK it is advisable to have some powerful hardware, like an 8-core cpu with 16GB of RAM will absolutely work.

Installation
------------
TTS and TTS_GTK is working with Ubuntu 18.04 (or newer) with python >= 3.7, < 3.11..

If you don't have Python3 installed, start with that:
```sudo apt install python3```

Then install TTS with:
```pip3 install TTS```

And last: download or git clone the TTS_GTK project, releases: <https://github.com/technout/tts_gtk/releases>

Extract the files and run tts_gtk.py from the project directory (from the command line: ```python3 /path/to/file/tts_gtk.py```)

Good to know: tts_gtk.py needs read and write access to the project directory. The default project directory is pointing to: /home/{current_user}/python/ttsgui/audio/
This directory can be changed in line 107 of tts_gtk.py

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
        The default workable value now 40 words.
        This can be changed in newer releases.
```
License
-------
TTS_GTK is released under the same terms of the Mozilla Public License 2.0 (as well for TTS). Please refer to the LICENSE file.
