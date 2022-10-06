# TTS_GTK
Graphical interface for Coqui TTS (Text to Speech) command line. Made in GTK3 and Python3 for the Linux platform.

This program uses the [Coqui TTS](https://github.com/coqui-ai/TTS) software for converting text to speech. This is a very interesting project and is constantly updated and improving fast. But it still has some limitations. You can use it from command line or install it as a server. I decided to add a third option: A GTK3 graphical interface. I also added multithreading support and use all the cpu cores you have, while audio is playing, the next lines of text will be processed in the background. I started this project so i can copy and paste some text from the web and let the computer read it to me, after a while this first beta version came to life. But still a work in progress, you can add to the project as well, help me improve it faster.

Language support: English, German, Spanish, Italian and some other languages have voice models (See Coqui TTS)

The sentence read out as audio is visible as the blue text:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_1.png)

You can also change some parameters (like the audio speed or the voice model) with extra options, some examples:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_2.png)

Requirements
------------
For running TTS or TTS_GTK it is advisable to have some powerful hardware, like an 8-core cpu with 16GB of RAM will absolutely work.

Installation
------------
TTS and TTS_GTK is working with Ubuntu 18.04 (or newer) with python >= 3.7, < 3.11..

If you don't have Python3 installed, start with that:
```sudo apt install python3```

Then install TTS with:
```pip install TTS```

And last: download or git clone the TTS_GTK project, releases: <https://github.com/technout/tts_gtk/releases>

Extract the files and run tts_gtk.py from the project directory (form the command line: ```python3 /path/to/file/tts_gtk.py```)

Good to know: tts_gtk.py needs read and write access to /home/{current_user}/python/ttsgui/audio/
This working directory can be changed in line 70

License
-------
TTS_GTK is released under the same terms of the Mozilla Public License 2.0 (as well for TTS). Please refer to the LICENSE file.
