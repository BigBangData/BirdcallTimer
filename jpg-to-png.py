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


# convert jpg to png
import os
from PIL import Image

path = os.path.join("img", "ebird")

for img in os.listdir(path):
    ebird_code = img.split(".")[0]
    jpg = os.path.join(path, img)  
    image = Image.open(jpg)  
    png = os.path.join(path, ".".join([ebird_code, "png"]))
    image.save(png)

# delete jpgs with $ rm *.jpg (in /img/ebird/)