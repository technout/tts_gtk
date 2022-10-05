# TTS_GTK
Graphical interface for Coqui TTS (Text to Speech) command line. Made in GTK3 and Python3 for the Linux platform.

This program uses the [Coqui TTS](https://github.com/coqui-ai/TTS) software for converting text to speech. This is a very interesting project and is constantly updated and improving fast. But it still has some limitations. You can use it from command line or install it as a server. I decided to add a third option: A GTK3 graphical interface. I also added support and use of all the cpu cores you have, the text will be processed in the background while the first sentence will be soon to hear as an audio clip.

The sentence read out as audio is visible as the blue text:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_1.png)

You can also change some parameters (like the audio speed or the voice model) with extra options, some examples:
![Screenshot](https://github.com/technout/tts_gtk/blob/main/screen_tts_gtk_2.png)

For running TTS or TTS_GTK it is advisable to have some powerful hardware, like an 8-core cpu with 16GB of RAM will absolutely work.
