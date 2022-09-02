import board
import neopixel
pixels = neopixel.NeoPixel(board.D12, 2)


import time


pixels[0] = (128,128,0)
pixels[1] = (128,128,0)

while 1:
	time.sleep(1)