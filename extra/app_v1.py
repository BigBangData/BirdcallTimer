#!/usr/bin/env python

# Copyright 2021 Marcelo Sanches
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import html
import time 
import random

import wave
import pyaudio
import pandas as pd
#import multiprocessing
import concurrent.futures as cf

from datetime import datetime
from tkinter import Label, Tk, Canvas, PhotoImage


def validate_number(raw_num, typeof):
    if typeof == "float":
        try:
            num = float(raw_num)
            assert 0 <= num <= 90
        except ValueError as e:
            print("Error: <mins> must be an integer or float")
            sys.exit()
        except AssertionError as e:
            print("Error: <mins> must be between 0 and 90 inclusive")
            sys.exit()
    else:
        try:
            num = int(raw_num)
            assert 1 <= num <= 10
        except ValueError as e:
            print("Error: <times> must be an integer")
            exit(1)
        except AssertionError as e:
            print("Error: <times> must be between 1 and 10 inclusive")
            exit(1)

    return num


def check_args():
    
    # error types
    no_args=f"Error: must supply three arguments\nUsage:\n\
$ bash run.sh <(sit, stand)> <mins (0-90)> <mins (0-90) \
<times (1-10)>\nExample: bash run.sh sit 45 10 3\n\
         (sit first, sit 45 mins, stand 10 mins, 3 times)"

    arg1="Error: <first_action> must be either 'sit' or 'stand'"

    # not 4 arguments 
    if len(sys.argv) != 5:
        print(no_args)
        sys.exit()
    # first arg not "sit" nor "stand"
    elif sys.argv[1].lower() not in ["sit", "stand"]:
        print(arg1)
        sys.exit()
    # validate number args
    else:
        first_action = sys.argv[1]
        mins1 = validate_number(sys.argv[2], "float")
        mins2 = validate_number(sys.argv[3], "float")
        times = validate_number(sys.argv[4], "int")
        
    return first_action, mins1, mins2, times

    
def get_time():
    """Get the date and time."""
    dt_object = datetime.fromtimestamp(time.time())
    d, t = str(dt_object).split('.')[0].split(' ')
    return d, t


def get_info(rand):
    """Returns info for a specific recording.
    
    Params:
    ------
    rand -- a random integer for the wave files
    
    Info:
    -----
    XCode -- specific code, append to https://xeno-canto.org 
             to get specific recording 
    Ebird Code -- the abbreviated bird species code
                  also the name of the sub directories
    Bird Species -- the full bird species name 
    Recorded On -- date of recording 
    Recorded In -- country of recording
    """
    rwave = waves[rand]
    rcode = codes[rand]
    rdf = df[df['xc_id'] == int(rcode)]
    rix = rdf.index[0]

    ebird_code = rdf['ebird_code'][rix]
    bird_species = rdf['species'][rix]
    rec_date = rdf['date'][rix]
    country = rdf['country'][rix]
    info = f'\nXCode: {rcode}\nEbird Code: {ebird_code}\nBird Species: {bird_species}\
\nRecorded On: {rec_date}\nRecorded In: {country}\n'

    rebird = pic_df['ebird_code'] == ebird_code
    rurl = pic_df['url'][rebird].values[0]
    rcopy = pic_df['copyright'][rebird].values[0]
    pic_info = f'\n{rurl}\n(c) {rcopy}\n'

    return info, rwave, pic_info


def display_popup(msg, info, pic_info):
    """Display a self-destructing popup msg."

    Args:
    -----
    msg -- time, stand or sit message
    info -- basic info about the recording
    
    TODO: add a picture of bird  
    """
    # instantiate Tkinter
    root = Tk()
    
    # prepare prompt
    prompt = '\n'.join([msg, info, pic_info])
    label = Label(root, text=prompt, width=len(msg))
    canvas = Canvas(root, width=480, height=320, bg='black')
    label.pack(); canvas.pack()

    # grab image
    ebird_code = info.split(":")[2].split("\n")[0].strip()
    filepath = os.path.join("img", "ebird", ".".join([ebird_code, "png"]))
    pic = PhotoImage(file=filepath)
    canvas.create_image(240, 160, image=pic)

    # display at topmost layer 
    root.attributes("-topmost", True)

    # destroy image...
    def popup_box():
        root.destroy()

    # ...after 10 secs
    root.attributes("-topmost", True)
    root.after(3000, popup_box)
    root.mainloop()


def play_audio(info, rwave):
    """Play a bird call for 10 seconds.
    
    Args:
    -----
    info -- basic info about the recording
    rwave -- random wave file path for audio playback    
    """

    print(info)

    chunk = 1024

    wf = wave.open(rwave, 'rb')

    # instantiate PyAudio
    p = pyaudio.PyAudio()

    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(chunk)

    # play stream
    T1 = time.time()
    
    # while len(data) > 0:
    # rather, for 10 secs
    while time.time() - T1 < 3:
        stream.write(data)
        data = wf.readframes(chunk)
    
    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


def run_procs(msg):
    """Run both popup and audio processes simultaneously.
        Uses concurrent.futures wrapper for multiprocessing.
    """
    rand = random.randint(1, len(waves)-1)
    info, rwave, pic_info = get_info(rand)

    with cf.ProcessPoolExecutor(max_workers=2) as executor:
        p1 = executor.submit(play_audio, info, rwave)
        p2 = executor.submit(display_popup, msg, info, pic_info)


#def run_async(msg):
#    """Run both popup and audio processes simultaneously.
#        Uses multiprocessing module directly.
#    """
#    rand = random.randint(1, len(waves)-1)
#    info, rwave, pic_info = get_info(rand)
#
#    p1 = multiprocessing.Process(target=play_audio, args=(info, rwave))
#    p2 = multiprocessing.Process(target=display_popup, args=(msg, info, pic_info))
#
#    p1.start(); p2.start()
#    p1.join(); p2.join()

        
def move_user(direction):
    """Message user to stand up or sit down:
    1. Playing a birdsong to get user's attention.
    2. Printing instructions to the console.
    3. Make a popup dialog box appear with info.
    """
    if direction == "up":
        # get time 
        day, now = get_time()
        msg = f'{now} - If you\'d be so kind as to stand now. Much appreciated!'
        print(msg)
        # play audio, popup box, wait 
        run_procs(msg)
        #run_async(msg)
        time.sleep(stand_sec)       
    else:    
        # get time        
        day, now = get_time()
        msg = f'{now} - That was FANTASTIC work! You may sit now.'
        print(msg)
        # play audio, popup box, wait        
        #run_procs(msg)
        run_async
        time.sleep(sit_sec)
        

if __name__ == '__main__':
    
    # check args
    first_action, mins1, mins2, times = check_args()

    # read metadata
    df = pd.read_csv(os.path.join("config", "metadata.csv"))
    pic_df = pd.read_csv(os.path.join("config", "pic_metadata.csv"))

    wav_dir = os.path.join("audio", "wav")
    waves, codes = [], []

    for subdir in os.listdir(wav_dir):
        for wav in os.listdir(os.path.join(wav_dir, subdir)):
            waves.append(os.path.join(wav_dir, subdir, wav))
            codes.append(wav.split('.')[0][2:])
        
    # escape html --- add to check_args
    #username = html.escape(raw_username)
    #sit_min = html.escape(raw_sit_min)
    #stand_min = html.escape(raw_stand_min)
    #times = html.escape(raw_times)    

    # validate usernname
    #username = str(username)
    #try:
    #    assert 1 <= len(username) <= 25
    #except AssertionError as e:
    #    print("Error: 'username' must be at least 1 and at most 25 characters long.")
    #    sys.exit(1)

    # set sitting vs standing mins
    if first_action == "sit":
        sit_min = mins1
        stand_min = mins2
    else:
        stand_min = mins1
        sit_min = mins2
    
    # calculate secs
    sit_sec = sit_min*60
    stand_sec = stand_min*60
    
    # start work session
    print(f'\nThank you, your wish is my command.\nPlease {first_action}.\n')
    day, start_time = get_time()
    print(f'Day: {day}')
    print(f'Start time: {start_time}\n')
    
    if first_action == "sit":
        time.sleep(sit_sec)
    else:
        time.sleep(stand_sec)
    
    # repeat 'times' times
    for i in range(times):
        if i+1 == times:
            if first_action == "sit":
                move_user('up')
            else:
                move_user('down')                
        else:
            if first_action == "sit":            
                move_user('up')
                move_user('down')
            else:
                move_user('down')
                move_user('up')
                
    # end work session
    day, end_time = get_time()
    msg = f'{end_time} - Excellent work all around, how about that break?'
    print(msg)
    
    # play audio, popup box
    #run_procs(msg)
    run_async(msg)