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


# Ad Hoc Handling Data

# Some ad hoc data examination and processing steps.
import os
import subprocess
import pandas as pd

# list all waves and codes
wav_dir = os.path.join("audio", "wav")
waves, codes = [], []

for subdir in os.listdir(wav_dir):
    for i, wav in enumerate(os.listdir(os.path.join(wav_dir, subdir))):
        waves.append(os.path.join(wav_dir, subdir, wav))
        codes.append(wav.split('.')[0][2:])

# load chosen recordings
cs_path = os.path.join("config", "chosen.csv")
cs = pd.read_csv(cs_path)

# purge all wave files that are not chosen 
wav_dir = os.path.join("audio", "wav")
waves, codes = [], []

for subdir in os.listdir(wav_dir):
    for wav in os.listdir(os.path.join(wav_dir, subdir)):
        if int(wav.split('.')[0][2:]) in set(cs['code']):
            continue
        else:
            os.remove(os.path.join(wav_dir, subdir, wav))

# remove empty dirs
wset = list()
for wav in waves:
    wset.append(wav.split("\\")[2])

if wset: # if wset isn't empty 
    for subdir in os.listdir(wav_dir):
        if subdir not in set(wset):
             os.rmdir(os.path.join(wav_dir, subdir))

# looking at metadata
df_path = os.path.join("config", "metadata.csv")
df = pd.read_csv(df_path)

df.iloc[:3,:13]
df.iloc[:3,13:23]
df.iloc[:3,23:]
    

# listen to audio in jupyter
for subdir in os.listdir(wav_dir):
    for i, wav in enumerate(os.listdir(os.path.join(wav_dir, subdir))):
        waves.append(os.path.join(wav_dir, subdir, wav))
        codes.append(wav.split('.')[0][2:])

waves[0]

import IPython.display as ipd
ipd.Audio(waves[0])
