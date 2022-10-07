#! /usr/bin/env python
#  -*- coding: utf-8 -*-
# 
# Made by Technout <https://github.com/technout>
# GTK interface build with Glade 3.40
# Copyright (c) 2022
# First version from 2022.01.08
# 
# TODO:
# finetune: processing of first line
# shortcut keys for playing audio
# set maximum waitingtime for audio
# choose the voice
# choose language
# number all sentences, as optional
# search in text
# Replace golbal UID with parameters
# Queue multiple sentences and enable to save
# Filter sentence starting with '<space> or "<space>
# except KeyboardInterrupt
# add css classes for gtk
# adding help button with help text
# add list of models, read from https://github.com/coqui-ai/TTS/blob/dev/TTS/.models.json

# BUGS: 
# Many still left

__version__ = "0.5-2022.10.07"

# from curses import window
import logging
# from typing_extensions import Self
logging.basicConfig(level=logging.DEBUG, filename='tts_gtk.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

import os
import gi
import re
import sys
import psutil
import subprocess
import glob
# import shutil
import getpass
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import argparse
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # disable pygame welcome message
import pygame.mixer
from pydub import AudioSegment
import pyrubberband as pyrb
import soundfile as sf
# from pydub.playback import play
import random
# from tkinter.constants import *
from pathlib import Path
import threading
# import multiprocessing
from multiprocessing import Process, current_process, Lock
# from queue import Empty, Queue

class Tts_gtk():
    def __init__(self, *args):
        global builder, Queuelist
        global wav_output_dir, filename, MyUIDs, UID, handlers, PlaySound, TextList, AddtoQueue
        global WaitingList, ProcessLock, PlayingLock
        global project_directory

        builder = Gtk.Builder()
        # builder.add_from_file(f'/home/{getpass.getuser()}/python/ttsgui/tts_gtk.glade')
        builder.add_from_file('tts_gtk.glade')
        handlers = {
            "onDestroy": self.onDestroy,
            "btnPlayClicked": self.btnPlayClicked,
            "btnSendClicked": self.btnPlayClicked,
            "btnPauseClicked": self.btnPauseClicked,
            "btnStopClicked": self.btnStopClicked,
            "btnClearClicked": self.btnClearClicked,
            "btnInfoClicked": self.btnInfoClicked,
            "btnInlineClicked": self.btnInlineClicked,
            "btnFormatClicked": self.btnFormatClicked,
            "btnSaveClicked": self.btnSaveClicked,
            "btnRePlayClicked": self.btnRePlayClicked,
            "btnQueueClicked": self.btnQueueClicked,
            "txtFieldChange": self.txtFieldChange,
            "QueueChecked": self.btnQueueChecked,
            "text_paste_handler": self.text_paste_handler
        }
        builder.connect_signals(handlers)
        window = builder.get_object("window1")
        window.set_title(f'TTS_GTK {str(__version__)}')
        window.connect("destroy", Gtk.main_quit)
        # window.connect("destroy", onDestroy) # todo
        # window.set_application()
        # builder.after(1, 0)

        # my globals
        UID = 0
        MyUIDs = [333333]
        TextList = []
        WaitingList = []
        PlaySound = True
        AddtoQueue = True
        Queuelist = SoundQueue()
        # QueuePlaying = Queue()
        # QueueProcessing = Queue()
        ProcessLock = Lock()
        PlayingLock = Lock()
        # wav_output_dir = f'/home/{getpass.getuser()}{project_directory}/audio/'
        # project_directory = "/python/tts_gtk"
        wav_output_dir = './audio/'
        if not os.path.exists(wav_output_dir):
            os.makedirs(wav_output_dir)
        os.chdir(wav_output_dir)
        print(f'Working directory: {os.getcwd()}')
        filename = 'tts_speech'

        # within gtk mainloop call this function:
        GLib.timeout_add(500, self.update_ram_status) # every 500 ms
        # GLib.timeout_add(550, self.update_speaker_label)

        window.show_all()
        deleteOldFiles(MyUIDs)
        Gtk.main()

    def onDestroy(self, *args):
        deleteOldFiles(MyUIDs) # todo: does this work?
        Gtk.main_quit

    def on_info_clicked(self, *args):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f'Information about TTS_GTK {__version__}',
        )
        dialog.format_secondary_text(
            """Made by Technout <https://github.com/technout>
            GTK interface build with Glade 3.40
            Copyright (c) 2022
            First version created: 2022.01.08
            
            Extra options you can use:
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
            """
        )
        dialog.run()
        dialog.destroy()

    def btnPlayClicked(self, *args):
        sText = getText()
        sText = tInline(sText)
        if len(sText) > 0:
            sText = escapeQuotes(sText)
            add_to_text_processing(sText)
            sText = placeLineBreaks(sText)
            threading.Thread(target=makeAudio, args=(sText,)).start()
        time.sleep(0.1)
        self.btnClearClicked(self)

    def btnRePlayClicked(self, *args):
        global PlaySound
        PlaySound = True
        dict_Params = getExtraParam() # [voicemodel, min_words, max_words, fplayspeed, crossfade]
        # tpr = threading.Thread(target=replayAudio, args=(gUID, dict_Params['fplayspeed'])).start()
        replayAudio(UID, dict_Params['fplayspeed'])

    def btnQueueClicked(self, *args):
        # position = builder.get_object("processing_scroll").get_vadjustment()
        # # set_lblstatus(f'pos v: {str(position.get_value())}')
        # position.set_value(position.get_value() + 5000)
        # builder.get_object("processing_scroll").set_vadjustment(position)
        pass

    def btnQueueChecked(self, *args):
        global AddtoQueue
        AddtoQueue = builder.get_object("queue_check").get_active()
        # Your text: (Ctrl + V paste and process text directly)
        if AddtoQueue:
            builder.get_object("lbl_your_text").set_text('Your text: (Ctrl + V process text directly)')
        else:
            builder.get_object("lbl_your_text").set_text('Your text:')
        setTextFieldFocus()

    def btnPauseClicked(self, *args):
        global PlaySound
        PlaySound = setPause()

    def btnStopClicked(self, *args): # todo: implement a better way to stop!
        global PlaySound
        pygame.mixer.music.stop()
        PlaySound = False
        setTextFieldFocus()

    def btnClearClicked(self, *args):
        global AddtoQueue
        tbuffer = getBuffer()
        tbuffer.delete(tbuffer.get_start_iter(), tbuffer.get_end_iter())
        if AddtoQueue:
            updTextCounter()
        setTextFieldFocus()

    def btnInfoClicked(self, *args):
        self.on_info_clicked()

    def btnInlineClicked(self, *args):
        textInline()

    def btnFormatClicked(self, *args):
        textFormat()

    def btnSaveClicked(self, *args): # todo: saving to file
        global UID
        source = filename + str(UID) + ".wav"
        # if gUID > 0:
        # wavfile = on_save_clicked()
        # if not wavfile == None:
        #     shutil.copy(source, wavfile)
        setTextFieldFocus()

    def txtFieldChange (self, *args):
        updTextCounter()

    def text_paste_handler(self, *args):
        if AddtoQueue:
            self.btnPlayClicked(self)

    # wrapper around function to call itself every 500 ms
    def update_ram_status(self):
        self.set_lblRamStatus()
        self.set_lblstatus()
        self.set_pause_status()
        self.update_speaker_label()
        # GLib.timeout_add(500, self.update_ram_status)
        return GLib.SOURCE_CONTINUE # better then recursive calling it self, i think

    def update_speaker_label(self):
        self.print_speaker_line()
        # GLib.timeout_add(600, update_speaker_label)

    def set_lblstatus(self):
        builder.get_object("lbl_status").set_text(f'Status: {Queuelist.get_status()}')

    def set_pause_status(self):
        if PlaySound:
            builder.get_object("lbl_paused").set_text('')
        else:
            builder.get_object("lbl_paused").set_text('< Paused >')

    def set_lblRamStatus(self):
        builder.get_object("lbl_ram_status").set_text(f'Avail RAM: {str(int(psutil.virtual_memory().available/1024**2))} MiB')

    def print_speaker_line(self):
        if not Queuelist.out_of_bound():
            position = Queuelist.get_position() - 1
            if position < 0: position = 0
            line = TextList[position]
            self.set_lblSpeak(f'Say: {line}')
        elif Queuelist.is_last_playing():
            Queuelist.set_last_playing(False)
            # gQueuelist.set_playing(False)
            position = Queuelist.get_position()
            line = TextList[position-1]
            self.set_lblSpeak(f'Say: {line}')

    def set_lblSpeak(self, text):
        builder.get_object("lbl_speak").set_text(text)

def set_text_processing(text):
    builder.get_object("txtbuffer_processing").set_text(text)
    updProccesTextCounter()

def add_to_text_processing(text):
    oldText = getProcessText()
    if len(oldText) > 0:
        oldText += '\n\n'
    builder.get_object("txtbuffer_processing").set_text(oldText + text)
    updProccesTextCounter()

def scrolldown_text():
    time.sleep(0.3)
    # builder.get_object("process_text_adjust").value = 90 # .get_vadjustment() processing_scroll
    position = builder.get_object("processing_scroll").get_vadjustment()
    # position = builder.get_object("process_text_adjust").get_value()
    position.set_value(position.get_value() + 5000)
    builder.get_object("processing_scroll").set_vadjustment(position)
    # builder.get_object("process_text_adjust").set_value(100)
    # set_lblstatus(f'pos v: {str(position)}')

def updProccesTextCounter():
    sText = getProcessText()
    chars = getProcessBuffer().get_char_count()
    builder.get_object("lblCharCount").set_text(f'Chars: {str(chars)} / Words: {str(len(sText.split()))}')

def getExtraParam():
    # the default values
    max_words = 40 # todo: New TTS 0.8 release can do much more! 14 words at max was the limit for TTS 0.7
    min_words = 13 # todo: still needed?
    fplayspeed = 1
    crossfade = 60 # in ms
    # voicemodel = 'tts_models/en/ljspeech/tacotron2-DDC'
    voicemodel = 'tts_models/en/ljspeech/vits' # better voice
    txtExtra = builder.get_object("txtExtra")
    extraPartam = txtExtra.get_text()
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_words', nargs='?')
    parser.add_argument('--min_words', nargs='?') # todo: still needed?
    parser.add_argument('--playspeed', nargs='?')
    parser.add_argument('--crossfade', nargs='?')
    parser.add_argument('--voicemodel', nargs='?')
    if len(extraPartam) > 1:
        args, unknown = parser.parse_known_args(extraPartam.split(" "))
        if args.max_words is not None:
            if args.max_words.isdigit():
                max_words = int(args.max_words)
        if args.min_words is not None:
            if args.min_words.isdigit():
                min_words = int(args.min_words)
        if args.playspeed is not None:
            if args.playspeed.replace('.', '', 1).isdigit():
                fplayspeed = float(args.playspeed)
                if fplayspeed > 1.9: fplayspeed = 1.9
                elif fplayspeed < 0.2: fplayspeed = 0.2
        if args.crossfade is not None:
            if args.crossfade.isdigit():
                crossfade = int(args.crossfade)
        if args.voicemodel is not None: voicemodel = args.voicemodel
    return {'voicemodel': voicemodel, 'min_words': min_words, 'max_words': max_words, 'fplayspeed': fplayspeed, 'crossfade': crossfade}

def clearText(*args):
    tbuffer = getBuffer()
    tbuffer.delete(tbuffer.get_start_iter(), tbuffer.get_end_iter())
    builder.get_object("txtField").grab_focus()

def escapeQuotes(sText):
    # replace different types of unicode/utf-8 quotes to universal double quotes
    sText=re.sub(r"[\u00AB\u2039\u203A\u00BB\u201C\u201D\u201E\u0022\"]", '\"', sText)
    sText=re.sub(r"[\u0060\u00B4\u2018\u2019\']", "\'", sText)
    # sText = sText.replace("'", "\'")
    # sText = sText.replace('"', '\"')
    return sText

def getText():
    tbuffer = getBuffer()
    return tbuffer.get_text(tbuffer.get_start_iter(), tbuffer.get_end_iter(), True)

def getBuffer():
    return builder.get_object("textbuffer1")

def getProcessText():
    tbuffer = getProcessBuffer()
    return tbuffer.get_text(tbuffer.get_start_iter(), tbuffer.get_end_iter(), True)

def getProcessBuffer():
    return builder.get_object("txtbuffer_processing")

# todo: use regex, so no big numbers will be split into lines
def placeLineBreaks(sText):
    sText = sText.replace('.', '.\n')
    sText = sText.replace(',', ',\n')
    sText = sText.replace('!', '!\n')
    sText = sText.replace('?', '?\n')
    sText = sText.replace(':', ':\n')
    sText = sText.replace(';', ';\n')
    sText = sText.replace('(', '\n(')
    sText = sText.replace(')', ')\n')
    # sText = re.sub("\s*(\W)\s*",r"\1", sText)
    return sText

def lowRAM():
    # max_processes = os.cpu_count()
    # mem_per_process = 600
    swap = psutil.swap_memory().percent
    if swap > 90:
        return True
    mem_available = psutil.virtual_memory().available
    if mem_available < 3000*1024**2: # Return True if lower then 3GB
        return True
    return False

def num_processes():
    count = 0
    proc_iter = psutil.process_iter(attrs=["name"])
    for p in proc_iter:
        if "tts" in p.info["name"]:
            if p.is_running():
                count += 1
    return count

### Run in new thread!
def processText(textlist, voicemodel, UID):
    # global gQueuelist, gProcessLock
    ProcessLock.acquire()
    # gQueuelist.set_processing(True)
    subproc = []
    pdone = 0
    # max_processes = os.cpu_count() - 1
    max_processes = 2
    # set_lblstatus('Status: Processing text..') # todo: remove all gtk reference from threads!
    iLines = len(textlist)
    Queuelist.set_status(f'Processing {str(iLines)} text lines..')
    for i in range(iLines):
        # this uses a lot of cpu/gpu power!!
        # Use .Popen for non waiting processes, in all other cases use .run
        # Shell=False: no shell needed, sent arguments as a list!
        # subproc[i] = subprocess.Popen(f"tts --text '{textlist[i]}' --out_path '{filename}{str(UID)}_{str(i)}.wav'", \
        #     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # old way with shell
        subproc.append(subprocess.Popen(['tts', '--text', textlist[i], '--model_name', voicemodel, '--out_path', filename + str(UID) + '_' + str(i) + '.wav'], \
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        print(f"- Process: '{textlist[i]}'")
        sys.stdout.flush()
        time.sleep(2)
        # if i > (5 + pdone):
        #     print('sleep 4')
        #     sys.stdout.flush()
        #     time.sleep(3)
        # todo: optimize for new TTS 0.8 release! (can process big lines of text)
        while num_processes() >= max_processes:
            print('sleep 3 - max_processes')
            sys.stdout.flush()
            time.sleep(3)
            for p in subproc:
                if p.poll() is not None:
                    pdone += 1
        while lowRAM():
            print('sleep 3 - lowRAM')
            sys.stdout.flush()
            time.sleep(3)
            for p in subproc:
                if p.poll() is not None:
                    pdone += 1
        pdone = 0
        # mem = 0
        for p in subproc:
            # for every process that is still running, add 1
            if p.poll() is not None:
                pdone += 1
        #         # print(f'_Subpro: {str(pdone)}, {str(p)}')
        #         try:
        #             # mem += psutil.Process(p.pid).memory_info().rss
        #             print(f'ProcessID: {str(p.pid)}')
        #         except psutil.NoSuchProcess:
        #             pass
        # print(f'Memory usage: {str(mem/1024**2)}')
        # print(f'RAM Avail: {str(not(lowRAM()))}')
        # print(f'RAM Usage: {str(num_processes()*600)} MiB')
        # set_lblRamStatus()
        print(f'RAM available: {str(int(psutil.virtual_memory().available/1024**2))} MiB; Swap usage: {str(psutil.swap_memory().percent)} %')
        sys.stdout.flush()
    ProcessLock.release()
    # gQueueProcessing.task_done()
    # gQueuelist.set_processing(False)
    print('processText done')
    Queuelist.set_status('Processing text to audio done')
    # set_lblstatus('Status: Processing text to audio done')

# todo: do not split a sentence in the middle of a big numbers, like in 600,000
"""returns list of lines, seperated by \n and not longer then maxlength"""
def splitText(sText, maxlength):
    alltext = sText.split("\n")
    iLines = len(alltext)-1
    punctuations = '\n.\n,\n!\n?\n:\n;\n(\n)\n \n'
    space = ' '
    n = 0  # first sentence
    while True:
        if len(alltext[n]) < 1: # delete sentence when too short
            alltext.pop(n)
            iLines -= 1
        else:
            row = alltext[n].split(" ") # split to words
            alltext[n] = " ".join(filter(None, row)) # join only non empty words
            if len(row) > maxlength:  # split the sentence, if too long
                if (round(len(row)/2)) > maxlength:
                    # if row is longer then 2x max
                    part1 = " ".join(row[0:maxlength])
                    part2 = " ".join(row[maxlength:])
                else:
                    part1 = " ".join(row[0:round(len(row)/2)])
                    part2 = " ".join(row[round(len(row)/2):])
                alltext.pop(n)              # delete original too long sentence
                alltext.insert(n, part1)    # add back the first shorter part
                alltext.insert(n+1, part2)  # add back the rest of the sentence
                iLines += 1                 # and make total list items 1 bigger
            elif n > 0:
                w = alltext[n][-3:] # short sentences may be removed
                if w in punctuations:
                    if not space in w: # merge only non space chars
                        alltext[n] = alltext[n-1] + alltext[n]
                    n -= 1 # todo: less code lines?
                    iLines -= 1
                    alltext.pop(n)
                elif (len(alltext[n-1].split(" "))-1) < (maxlength - len(row)):
                    # merge with previous sentence if that is also small
                    alltext[n] = alltext[n-1] + space + alltext[n]
                    n -= 1
                    iLines -= 1
                    alltext.pop(n)
            alltext[n] = alltext[n].strip()
            print(f'T: \'{alltext[n]}\'')
            sys.stdout.flush()
        n += 1          # move to next sentence
        if n > iLines:  # break the loop after the last sentence
            break
    return alltext

def setLastdot(sText):
    punctuation = '.,!?:;()'
    w = sText[-1]
    return sText if w in punctuation else sText + '.'

def setText(sentences): # todo: maybe delete?
    sentences.strip()
    getBuffer().set_text(str(sentences))

def setTextFieldFocus():
    builder.get_object("txtField").grab_focus()

def textInline(*args): # todo: maybe delete?
    # sText = getText()
    # sText = tInline(sText)
    # clearText()
    # getBuffer.set_text(sText)
    updTextCounter()
    builder.get_object("txtField").grab_focus()
    sys.stdout.flush()

def tInline(sText):
    if len(sText) > 0:
        sText = sText.split('\n')
        # print('w: ' + str(words))
        alltext = ''
        for l in sText:
            alltext += l+' '
        alltext = alltext.strip()
        if len(alltext) > 0:
            alltext = setLastdot(alltext)
        # sys.stdout.flush()
        return alltext
    else:
        return sText

# todo: still needed?
def textFormat(*args):
    words = getText()
    c = 0
    alltext = ''
    for w in words:
        c += 1
        # print('w: ' + w)
        if '.' in w or ',' in w or '!' in w or '?' in w or ':' in w or ';' in w:
            alltext += w+'\n'
            c = 0
        elif '\n' in w:
            alltext += w
            c = 0
            print('w:(n) ' + w)
        elif c > 14:
            alltext += w+'\n'
            c = 0
        else:
            alltext += w+' '
    alltext = alltext.strip()
    clearText()
    getBuffer().set_text(alltext)
    updTextCounter()
    sys.stdout.flush()

def updTextCounter():
    sText = getText()
    chars = getBuffer().get_char_count()
    builder.get_object("lblChars").set_text(f'Chars: {str(chars)} / Words: {str(len(sText.split()))}')

### Run in new thread!
def replayAudio(UID, fplayspeed):
    global Queuelist
    if int(UID) > 0:
        wavfile = filename + str(UID) + ".wav"
        Queuelist.append(wavfile)
        Queuelist.set_status('Replaying the audio..')
        iLines = 4
        tpr = threading.Thread(target=Queuelist.auto_play, args=(iLines, fplayspeed,))
        tpr.start()
    else:
        print(f'Nothing to replay.. {str(UID)}')
    sys.stdout.flush()

def increasePlayback(wavfile, fplayspeed):
    # increase the playback speed of the audio by fplayspeed
    if not fplayspeed == 1:
        n = random.randrange(100,999)
        audio, samplerate = sf.read(wavfile)
        audio = pyrb.time_stretch(audio, samplerate, fplayspeed)
        audio = pyrb.pitch_shift(audio, samplerate, 2.0-fplayspeed)
        if wavfile[-4:] == '.wav': # remove .wav from filename
            wavfile = wavfile[:-4]
        wavfile = wavfile + '_' + str(n) + '.wav'
        sf.write(wavfile, audio, samplerate, format='wav')
        return wavfile
    else:
        return wavfile

### Run in new thread!
def playAllAudio(iLines, UID, fplayspeed):
    global Queuelist, AddtoQueue, PlayingLock
    PlayingLock.acquire()
    Queuelist.set_playing(True)
    print(f'Lines: {str(iLines)}')
    print(f'Audiospeed: {str(fplayspeed)}')
    # gQueuelist.set_status('Playing audio..')
    # set_lblstatus('Status: Playing audio..')
    # add audio files to the queue
    for n in range(iLines):
        wavfile = filename + str(UID) + '_' + str(n) + ".wav"
        Queuelist.append(wavfile)
    Queuelist.auto_play(iLines, fplayspeed)
    PlayingLock.release()
    # gQueuelist.set_playing(False)
    print('playAllAudio done')
    # gQueuelist.set_status('All audio played')
    # set_lblstatus('Status: All audio played')
    # gQueuelist.print_queue()

def setPause():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        playSound = False
    else:
        pygame.mixer.music.unpause()
        # pygame.mixer.music.play()
        playSound = True
    return playSound

### Run in new thread!
def mergeAudiofiles(iLines, UID, crossover):
        combined = AudioSegment.silent(duration=crossover)
        c = 0
        waitingtime = 500
        for n in range(iLines):
            wavfile = filename + str(UID) + '_' + str(n) + ".wav"
            while not Path(wavfile).is_file(): # waiting for wav file
                time.sleep(0.3)
                c += 1
                if c > waitingtime: break
            if c < waitingtime:
                sound = AudioSegment.from_file(wavfile)
                combined = combined.append(sound, crossfade=crossover) # todo: replace crossover with a remove silent function??
            else:
                c = 0
        combined.export(filename + str(UID) + ".wav", format="wav")

### Run in new thread!
def makeAudio(sText, *args):
    global MyUIDs, UID, TextList, PlaySound
    PlaySound = True
    UID = 0
    textlist = None
    if len(sText) > 0:
        UID = random.randrange(10000,99999)
        params = getExtraParam() # [voicemodel, min_words, max_words, fplayspeed, crossfade]
        textlist = splitText(sText, params['max_words'])
        TextList.extend(textlist)

        # gQueueProcessing.put(UID)
        # c = 0
        # # waiting in line if processText is already running..
        # while True:
        #     c += 1
        #     # check if a process is already running
        #     if gQueuelist.is_processing():
        #         if c < 2:
        #             # add currect thread to process waitinglist (one time only)
        #             gQueuelist.process_waiting_add(UID)
        #         time.sleep(0.1)
        #     else:
        #         # if no process waiting list, move on
        #         if gQueuelist.process_waiting_get_next() == None:
        #             gQueuelist.set_processing(True)
        #             break
        #         # if current thread is next process, remove if from waiting list, set processing on True and move on
        #         if UID == gQueuelist.process_waiting_get_next():
        #             gQueuelist.set_processing(True)
        #             gQueuelist.process_waiting_get_next(remove=True)
        #             break
        tpx = threading.Thread(target=processText, args=(textlist, params['voicemodel'], UID))
        tpx.start()
        # gQueueProcessing.get()

        # c = 0
        # # waiting in line if playAllAudio is already running..
        # while True:
        #     c += 1
        #     # check if a playAllAudio is already running
        #     if gQueuelist.is_playing():
        #         if c < 2:
        #             # add currect thread to playing waitinglist (one time only)
        #             gQueuelist.play_waiting_add(UID)
        #         time.sleep(0.1)
        #     else:
        #         # if no playing waiting list, move on
        #         if gQueuelist.play_waiting_get_next() == None:
        #             gQueuelist.set_playing(True)
        #             # set_lblSpeak('Say: ...')
        #             break
        #         # if current thread is next process, remove if from waiting list, set playing on True and move on
        #         if UID == gQueuelist.play_waiting_get_next():
        #             gQueuelist.set_playing(True)
        #             gQueuelist.play_waiting_get_next(remove=True)
        #             break

        # use treading instead of Process, because else pygame.mixer.music will not work..!
        tpa = threading.Thread(target=playAllAudio, args=(len(textlist), UID, params['fplayspeed']))
        tpa.start()
        
        tpm = threading.Thread(target=mergeAudiofiles, args=(len(textlist), UID, params['crossfade']))
        tpm.start()
        UID = UID
        MyUIDs.append(UID)
        scrolldown_text()
        tpx.join()
        tpa.join()
    # sys.stdout.flush()

def deleteOldFiles(myUIDs):
    audioFiles = glob.glob(f'{filename}*.wav')
    if len(myUIDs) < 1: myUIDs = [333333]
    if myUIDs[-1] < 1000: myUIDs[-1] = 333333
    # if int(myUIDs) < 1000: myUIDs = 333333
    for file in audioFiles:
        # if not str(myUIDs) in f:
        if not any(str(uid) in file for uid in myUIDs): # if filename does not contain any previous UID of this session
            # print(f'deleting {f}')
            wavFile = Path(file)
            if wavFile.is_file():
                wavFile.unlink(missing_ok=True)
    sys.stdout.flush()

# todo: maybe make it a singleton? class method or with static methods?
class SoundQueue:
    def __init__(self):
        self.__queuelist = []
        self.__position = 0
        self.__is_playing = False
        self.__is_processing = False
        self.__last_playing = False
        self.__play_waiting = [] # todo: remove?
        self.__process_waiting = [] # todo: remove?
        self.__status = 'Ready'
        pygame.mixer.init()

    def append(self, audio):
        self.__queuelist.append(audio)

    def clear(self):
        self.__queuelist.clear()
        self.__position = 0
        self.__is_playing = False
        self.__is_processing = False

    def get(self):
        if not self.out_of_bound():
            return self.__queuelist[self.__position]
        else:
            return None

    def get_list(self):
        return self.__queuelist

    def get_position(self):
        return self.__position

    def get_status(self):
        return self.__status

    def is_playing(self):
        return self.__is_playing

    def is_last_playing(self):
        return self.__last_playing

    def is_processing(self):
        return self.__is_processing

    def next(self):
        self.__position += 1
    
    # todo: only one instance simultaneously!
    def auto_play(self, iLines, fplayspeed):
        pos = self.__position
        while not self.out_of_bound():
            self.play_next(fplayspeed)
            if pos+iLines == self.__position:
                self.__last_playing = True
                # print(f'Last audio playing..!')
                # sys.stdout.flush()
        self.__status = 'All audio played'

    def play_all_queued(self, fplayspeed):
        self.set_pos(0)
        self.auto_play(fplayspeed)

    # check if player is not busy, queue not out of bound and no pause button is pressed, then play the audio
    # if checkFile is True, then also check if the audio file does exists
    # if waiting is True, keep waiting until all lights are green and play the audio
    def play_next(self, fplayspeed, checkFile=True, waiting=True):
        count = 1
        wavfile = self.get()
        if not wavfile == None:
            # print(f'deb: get-file: {wavfile}')
            while True: # emulate do-while loop in Python
                if not pygame.mixer.music.get_busy() and PlaySound:
                    if checkFile and not Path(wavfile).is_file(): # todo: what if file does not exist and will never be created?
                        count += 1
                    else:
                        wavfile = increasePlayback(wavfile, fplayspeed)
                        try:
                            pygame.mixer.music.load(wavfile)
                            pygame.mixer.music.play()
                            self.__is_playing = True
                            self.__status = 'Playing audio..'
                        except pygame.error as e:
                            print(f'Error: PyGame wavfile unknown: {str(e)}')
                        self.next()
                        print(f'**Waiting for file: {str(count/10)} sec')
                        print(f'play file: {wavfile}')
                        waiting = False
                sys.stdout.flush()
                time.sleep(0.1)
                if not waiting:
                    break

    def play_waiting_add(self, UID):
        self.__play_waiting.append(UID)

    def process_waiting_add(self, UID):
        self.__process_waiting.append(UID)

    def play_waiting_get_next(self, remove=False):
        if len(self.__play_waiting) > 0:
            return_uid = self.__play_waiting[0]
            if remove:
                self.__play_waiting.pop(0)
        else:
            return_uid = None
        return return_uid

    def process_waiting_get_next(self, remove=False):
        if len(self.__process_waiting) > 0:
            return_uid = self.__process_waiting[0]
            if remove:
                self.__process_waiting.pop(0)
        else:
            return_uid = None
        return return_uid

    def print_queue(self):
        for item in self.__queuelist:
            print(f'Q: {item}')
        print(f'Q length: {self.size()}')
        for item in self.__play_waiting:
            print(f'PlayW: {item}')
        print(f'PlayW length: {len(self.__play_waiting)}')
        for item in self.__process_waiting:
            print(f'ProcW: {item}')
        print(f'ProcW length: {len(self.__process_waiting)}')

    def out_of_bound(self):
        if self.__position >= self.size():
            # self.__is_playing = False
            return True
        else:
            return False

    def set_playing(self, playing=True):
        self.__is_playing = playing

    def set_last_playing(self, playing=False):
        self.__last_playing = playing

    def set_processing(self, processing=True):
        self.__is_processing = processing

    def set_pos(self, position=0):
        self.__position = position

    def set_status(self, status):
        self.__status = status

    def size(self):
        return len(self.__queuelist)



if __name__ == '__main__':
    tts_gtk = Tts_gtk()
