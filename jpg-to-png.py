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