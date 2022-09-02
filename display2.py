#!/usr/bin/python3

from PIL import Image,ImageDraw,ImageFont

import epaper
import time
import os

# apt-get install python3-pil
# apt-get install python3-pip
# pip3 install RPi.GPIO
# pip3 install spidev
# pip3 install waveshare-epaper


# color = 1 = white
# color = 0 = black
def clearScreen(epd, image, color):
	draw = ImageDraw.Draw(image)
	draw.rectangle((0, 0, epd.width, epd.height), fill = color)
	draw=image.transpose(Image.ROTATE_90)
	epd.display(epd.getbuffer(image))

#main

epd = epaper.epaper('epd2in9d').EPD()
epd.init()

print("init and Clear")


epd.Clear(0xFF)
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame

epd.ReadBusy()
clearScreen(epd, image, 1)
epd.ReadBusy()


print("done clear!")

bmp = Image.open(os.path.join('', 'meter.bmp'))
image.paste(bmp, (0,0))

draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
draw.text((10, 25), "world", font=font)
draw=image.transpose(Image.ROTATE_90)
epd.display(epd.getbuffer(image))

print("sleeping!")
epd.sleep()