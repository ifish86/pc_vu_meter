import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 2000)
duty=50
pwm.start(duty)
while 1:
	for x in range(0,100,1):
		pwm.ChangeDutyCycle(x)
		print(x)
		time.sleep(1.25)
	time.sleep(2)
	for y in range(100,0,-1):
		pwm.ChangeDutyCycle(y)
		print(y)
		time.sleep(1.25)
	time.sleep(2)