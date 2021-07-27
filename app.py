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
import concurrent.futures as cf

from datetime import datetime
from tkinter import Label, Tk, Canvas, PhotoImage


def validate_number(raw_num, typeof):
    """Validates numeric arguments.
    'mins' should be float between 0 and 90 inclusive
    'times' should be int between 1 and 10 inclusive

    Args:
    -----
    raw_num -- numeric argument to be validated
    typeof -- whether it should be a float or integer

    """

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
    """Check arguments passed to app.py script."""

    # error types
    no_args=f"Error: must supply three arguments\nUsage:\n\
$ bash run.sh <first_action {sit|stand}> <mins1 (0-90)> <mins2 (0-90)> \
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

    Args:
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
    rdf = rec_df[rec_df['xc_id'] == int(rcode)]
    rix = rdf.index[0]

    ebird_code = rdf['ebird_code'][rix]
    bird_species = rdf['species'][rix]
    rec_date = rdf['date'][rix]
    country = rdf['country'][rix]
    recordist = rdf['recordist'][rix]
    info = f'\nXeno-canto Catalogue Number: {rcode}\nEbird Code: {ebird_code}\
\nBird Species: {bird_species}\nRecorded On: {rec_date}\
\nRecorded In: {country}\nRecordist: {recordist}\n'

    rebird = pic_df['ebird_code'] == ebird_code
    rurl = pic_df['url'][rebird].values[0]
    rcopy = pic_df['copyright'][rebird].values[0]
    pic_info = f'\n{rurl}\n(c) {rcopy}\n'

    return info, rwave, pic_info


def display_popup(msg, info, pic_info):
    """Display a self-destructing popup msg.

    Args:
    -----
    msg -- time, stand or sit message
    info -- basic info about the recording
    pic_info -- picture attibution info

    """
    # instantiate Tkinter
    root = Tk()

    # prepare prompt
    prompt = '\n'.join([msg, info, pic_info])
    label = Label(root, text=prompt)
    canvas = Canvas(root, width=480, height=320, bg='black')
    label.pack(); canvas.pack()

    # grab image
    ebird_code = info.split(":")[2].split("\n")[0].strip()
    filepath = os.path.join("img", "ebird", ".".join([ebird_code, "png"]))
    pic = PhotoImage(file=filepath)
    canvas.create_image(240, 160, image=pic)

    # display at topmost layer
    root.attributes("-topmost", True)

    # destroy image afte 10 seconds
    def popup_box():
        root.destroy()

    root.after(10000, popup_box)
    root.mainloop()


def play_audio(info, rwave):
    """Play a bird call for 10 seconds.

    Args:
    -----
    info -- basic info about the recording
    rwave -- random wave file path for audio playback

    """
    print(info)
    # open .wav file
    wf = wave.open(rwave, 'rb')

    # instantiate PyAudio
    p = pyaudio.PyAudio()

    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    chunk = 1024
    data = wf.readframes(chunk)

    # play stream for 10 seconds
    T1 = time.time()

    while time.time() - T1 < 10:
        stream.write(data)
        data = wf.readframes(chunk)

    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()


def run_procs(msg):
    """Run both popup and audio processes simultaneously.
    Uses the concurrent.futures wrapper for multiprocessing.

    """
    rand = random.randint(1, len(waves)-1)
    info, rwave, pic_info = get_info(rand)

    with cf.ProcessPoolExecutor(max_workers=2) as executor:
        p1 = executor.submit(play_audio, info, rwave)
        p2 = executor.submit(display_popup, msg, info, pic_info)


def move_user(direction):
    """Message user to stand up or sit down:

    - Plays a random birdcall to get user's attention.;
    - Pops up a dialog box with a picture of the bird,
      information about the birdsong and picture,
      and instructions to sit or stand;
    - Prints to console;
    - Times waiting period.

    """
    if direction == "up":
        # get time
        day, now = get_time()
        msg = f'{now} - If you\'d be so kind as to stand now. Much appreciated!'
        print(msg)
        # play audio, popup box, wait
        run_procs(msg)
        time.sleep(stand_sec)
    else:
        # get time
        day, now = get_time()
        msg = f'{now} - That was FANTASTIC work! You may sit now.'
        print(msg)
        # play audio, popup box, wait
        run_procs(msg)
        time.sleep(sit_sec)


if __name__ == '__main__':

    # check args
    first_action, mins1, mins2, times = check_args()

    # read metadata
    rec_df = pd.read_csv(os.path.join("csv", "rec_metadata.csv"))
    pic_df = pd.read_csv(os.path.join("csv", "pic_metadata.csv"))

    wav_dir = os.path.join("audio", "wav")
    waves, codes = [], []

    for subdir in os.listdir(wav_dir):
        for wav in os.listdir(os.path.join(wav_dir, subdir)):
            waves.append(os.path.join(wav_dir, subdir, wav))
            codes.append(wav.split('.')[0][2:])

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
    run_procs(msg)
