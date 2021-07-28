#!/usr/bin/env python

# Adhoc fixes

import os
import pandas as pd


# wav files and Xcodes in audio/
wav_dir = os.path.join("audio", "wav")
subdirs, waves, codes = [], [], []

for subdir in os.listdir(wav_dir):
    subdirs.append(subdir)
    for i, wav in enumerate(os.listdir(os.path.join(wav_dir, subdir))):
        waves.append(os.path.join(wav_dir, subdir, wav))
        codes.append(wav.split('.')[0][2:])



print(f'There are {len(subdirs)} bird species and {len(waves)} recordings.')


chosen_path =  os.path.join("csv", "chosen.csv")
chosen_df = pd.read_csv(chosen_path)

from PIL import Image

pic_path = os.path.join("img", "ebird")

for img in os.listdir(pic_path):
    ebird_code, ext = img.split(".")
    if ext == "jpg":
        jpg = os.path.join(pic_path, img)  
        image = Image.open(jpg)  
        png = os.path.join(pic_path, ".".join([ebird_code, "png"]))
        image.save(png)
        os.remove(jpg)
    else:
        pass

len(os.listdir(pic_path))



rec_path = os.path.join("csv", "rec_metadata.csv")
rec_df = pd.read_csv(rec_path)



df = chosen_df.merge(rec_df.loc[:,("ebird_code","xc_id")], 
                     left_on='code', right_on='xc_id')

df.drop(["xc_id"], axis=1, inplace=True)


len(df)



chosen_df = df[df["ebird_code"].isin(subdirs)]


chosen_df.to_csv(chosen_path, index=False)


import subprocess

chosen_df = pd.read_csv(chosen_path)

chosen_df.head()


# get outstanding mp3 files and convert to wav files
# NB - assumes 1 recording per bird species!

mp3_dir = os.path.join("audio", "mp3")
wav_dir = os.path.join("audio", "wav")

for ec, c in zip(chosen_df['ebird_code'], chosen_df['code']):
    if ec not in subdirs:
        mp3_subdir = os.path.join(mp3_dir, ec)
        wav_subdir = os.path.join(wav_dir, ec)
        
        try:
            os.stat(wav_subdir)
        except FileNotFoundError:
            os.makedirs(wav_subdir)
            
        mp3 = ''.join([''.join(['XC', str(c)]), '.mp3'])
        wav = ''.join([''.join(['XC', str(c)]), '.wav'])

        mp3_filepath = os.path.join(mp3_subdir, mp3)
        wav_filepath = os.path.join(wav_subdir, wav)

        subprocess.call([
            'ffmpeg', '-hide_banner',
            '-loglevel', 'quiet',
            '-i', mp3_filepath, wav_filepath
        ])        




