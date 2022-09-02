#!/usr/bin/python3

from PIL import Image,ImageDraw,ImageFont

import epaper
import time
import os

import RPi.GPIO as GPIO

import urllib.request
import json
import math

import board
import neopixel
pixels = neopixel.NeoPixel(board.D12, 2)


# apt-get install python3-pil
# apt-get install python3-pip
# pip3 install RPi.GPIO
# pip3 install spidev
# pip3 install waveshare-epaper
# pip3 install rpi_ws281x adafruit-circuitpython-neopixel


	
# color = 1 = white
# color = 0 = black
def clearScreen(epd, image, color):
	#epd.init(epd.lut_full_update)
	epd.init()
	draw = ImageDraw.Draw(image)
	draw.rectangle((0, 0, epd.width, epd.height), fill = color)
	draw=image.transpose(Image.ROTATE_90)
	epd.display(epd.getbuffer(image))
	epd.ReadBusy()
	epd.sleep()
	GPIO.cleanup() 
	

def showVuMeter(epd, image, title, subtitle, rangeMin, rangeMax, units):
	#epd.init(epd.lut_full_update)
	epd.init()
	bmp = Image.open(os.path.join('', 'meter_fit2.bmp'))
	image.paste(bmp, (0,0))
	draw = ImageDraw.Draw(image)
	
	fontScale=1;
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", math.ceil(35/fontScale))
	while font.getsize(title)[0] > 200:
		fontScale=float(fontScale)+0.1
		font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", math.ceil(35/fontScale))
	draw.text((int((epd.height/2)-(font.getsize(title)[0]/2)), 60), title, font=font)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
	
	draw.text((10, 80), str(rangeMin), font=font)
	draw.text((int(epd.height-font.getsize(str(rangeMax))[0]-2), 80), str(rangeMax), font=font)
	
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
	
	if units != "":
		subtitle=subtitle+'('+units+')'
	draw.text((int((epd.height/2)-(font.getsize(subtitle)[0]/2)), 100), subtitle, font=font)
	
	draw=image.transpose(Image.ROTATE_90)
	epd.display(epd.getbuffer(image))
	epd.ReadBusy()
	epd.sleep()
	time.sleep(0.25)
	GPIO.cleanup() 


#main

pixels[0] = (192,128,1)
pixels[1] = (192,128,1)


#epd = epaper.epaper('epd2in9').EPD()
#epd.init(epd.lut_full_update)

epd = epaper.epaper('epd2in9d').EPD()
epd.init()

epd.Clear(0xFF)
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame


#clearScreen(epd, image, 1)
#print("done clear!")
#showVuMeter(epd, image, "Power", 0, 100, "%")
print("displaying Vu Meter")

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 1000)

#curl http://192.168.7.1:8085/data.json



GPIO.cleanup() 
#showVuMeter(epd, image, "CPU", 0, 100, "%")
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

#down
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#up
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm.start(0)

led="cool"

c=0
index=2
subindex=1
updateDisplay=True;

newVal=0
newMax=0
newMin=999999999
units="%"
dispMax=100
dispMin=0
m=1

title=""
subtitle=""
addr="192.168.7.1"

curMax=0
curMin=0

with urllib.request.urlopen('http://'+addr+':8085/data.json') as response:
	data = json.load(response)

while 1:
	if GPIO.input(23) == False:
		print('button 23 pushed!');
		index=index-1
		updateDisplay=True;
		while GPIO.input(23) == False:
			time.sleep(0.25)
		c=0
	if GPIO.input(24) == False and False:
		print('button 24 pushed!');
		index=index+1
		updateDisplay=True;
		while GPIO.input(24) == False:
			time.sleep(0.25)
		c=0
			
	if index < 0:
		subindex=subindex-1
		if subindex < 0:
			subindex=len(data['Children'][0]['Children'])-1
		index=len(data['Children'][0]['Children'][subindex]['Children'])-1;
	if index > len(data['Children'][0]['Children'][subindex]['Children'])-1:
		index=0
		
	if c == 0:
		with urllib.request.urlopen('http://'+addr+':8085/data.json') as response:
			data = json.load(response)
			temp = data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0]['Min'].split(' ')
			newMin = temp[0]
			temp = data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0]['Max'].split(' ')
			newMax = temp[0]
			
			if curMax != newMax or curMin != newMin or title != data['Children'][0]['Children'][subindex]['Children'][index]['Text']:
				curMin=newMin
				curMax=newMax
				updateDisplay=True
				title = data['Children'][0]['Children'][subindex]['Children'][index]['Text']
				subtitle = data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0]['Text']
				print(newMax+';'+newMin)
				print(";"+str(m)+";"+str(curMax)+";"+str(curMin))
				print(data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0])
				if newMax == newMin or newMax == "" or newMin == "":
					index=index-1
					continue
				m=float(100/(float(newMax)-float(newMin)))
				temp = data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0]['Value'].split(' ')
				if len(temp) > 1:
					units = temp[1]
				else:
					units = ""
				if units == "%":
					m=1
					dispMin=0
					dispMax=100
			temp = data['Children'][0]['Children'][subindex]['Children'][index]['Children'][0]['Value'].split(' ')
			newVal = temp[0]
			newVal = (float(newVal) - float(curMin)) * m
			value = math.ceil(float(newVal))
			if value > 100:
				value=100
			if value < 0:
				value=0
			#print(str(value)+";"+str(m)+";"+str(curMax)+";"+str(curMin))
			pwm.ChangeDutyCycle(value)
			if float(newMin) >= 0:
				dispMin=math.floor(float(newMin))
			else:
				dispMin=newMin
			if float(newMax) >= 10:
				dispMax=math.ceil(float(newMax))
			else:
				dispMax=newMax
			if units == "%":
				dispMin=0
				dispMax=100
	
	
	
	if updateDisplay:
		showVuMeter(epd, image, title, subtitle, dispMin, dispMax, units)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18, GPIO.OUT)
		GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	if int(value) >= 80 and led == "cool":
		led="hot"
		pixels = neopixel.NeoPixel(board.D12, 2)
		pixels[0] = (250,16,1)
		pixels[1] = (250,16,1)
		#time.sleep(1)
	elif int(value) < 80 and led == "hot":
		led="cool"
		pixels = neopixel.NeoPixel(board.D12, 2)
		pixels[0] = (192,128,1)
		pixels[1] = (192,128,1)
		#time.sleep(1)
	#print(str(value))
	time.sleep(0.01)
	c=c+1
	updateDisplay=False;
	if c > 64:
		c=0
	

while 0:
	GPIO.cleanup() 
	showVuMeter(epd, image, "Going Up", 0, 100, "%")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	pwm.start(0)
	for x in range(0,100,1):
		pwm.ChangeDutyCycle(x)
		print(x)
		time.sleep(2.25)
	time.sleep(2)
	GPIO.cleanup() 
	showVuMeter(epd, image, "Going Down", 0, 100, "%")
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	pwm.start(100)
	for y in range(100,0,-1):
		pwm.ChangeDutyCycle(y)
		print(y)
		time.sleep(2.25)
	time.sleep(0.1)
	c=c+1


print("Done!")

