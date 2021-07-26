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
import subprocess

mp3_dir = os.path.join("audio", "mp3")
wav_dir = os.path.join("audio", "wav")

for subdir in os.listdir(mp3_dir):

    mp3_subdir = os.path.join(mp3_dir, subdir)
    wav_subdir = os.path.join(wav_dir, subdir)
    
    try:
        os.stat(wav_subdir)
    except FileNotFoundError:
        os.makedirs(wav_subdir)
    
    for mp3 in os.listdir(mp3_subdir):
    
        wav = ''.join([mp3.split('.')[0], '.wav'])
        
        mp3_filepath = os.path.join(mp3_subdir, mp3)
        wav_filepath = os.path.join(wav_subdir, wav)

        subprocess.call([
            'ffmpeg', '-hide_banner', 
            '-loglevel', 'quiet', 
            '-i', mp3_filepath, wav_filepath
        ])