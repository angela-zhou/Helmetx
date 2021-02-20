# Code created by Hunter McCullagh and Janvi Patel
# References found at the bottom of file

# LIBRARIES
import time
import Adafruit_CharLCD as LCD
import smbus
import math
import RPi.GPIO as GPIO

# SETUP
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# buttons
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
btn1 = 23 # closer to pot
btn2 = 24
# helmet lights
GPIO.setup(4, GPIO.OUT)
# LCD screen
lcd_rs        = 21 
lcd_en        = 20
lcd_d4        = 26
lcd_d5        = 19
lcd_d6        = 13
lcd_d7        = 6
lcd_backlight = 4 
lcd_columns = 16
lcd_rows    = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_backlight)
# ultrasonic sensor
GPIO_TRIGGER = 17 #11
GPIO_ECHO = 27 #13
# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
# Velocity calculations
t = 1
vi = 14
# Constants & variables
dist_limit = 15
lightOn = 0
stats = 0

# Function that returns the distance using readings from the ultrasonic sensor
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance
#Acceleromter Addresses
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

#Accelerometer Functions
def read_byte(reg):
    return bus.read_byte_data(address, reg)


def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


bus = smbus.SMBus(1)  # bus = smbus.SMBus(0)
address = 0x68  # via i2cdetect

# Accelerometer function call
bus.write_byte_data(address, power_mgmt_1, 0)

#LCD functions
def clear_row(row):
    for i in range(16):
        lcd.set_cursor(i,row)
        lcd.message(" ")

def display_title(stats):
    lcd.clear()
    lcd.set_cursor(0,0)
    if stats == 0:
        lcd.message("Speed:")
    elif stats == 1:
        lcd.message("Acceleration:")
    elif stats == 2:
        lcd.message("Directions:")
    time.sleep(0.1)
    
def display_value(value):
    clear_row(1)
    lcd.set_cursor(0,1)
    lcd.message(value)
    time.sleep(0.1)

display_title(stats)

#Main Loop
while True:
    
    # Acceleration and Velocity Calculations
    accel_xout = read_word_2c(0x3b)/ 16384.0
    accel_yout = read_word_2c(0x3d)/ 16384.0
    accel_mag = math.sqrt(math.pow(accel_xout,2)+ math.pow(accel_yout,2))
    vf = vi + accel_mag * t
    vi = vf
    time.sleep(t)
    # RECHECK LOGIC OR METHOD
    
    # Toggle Button (btn1) for helmet lights (GPIO4)
    if GPIO.input(btn1) == GPIO.HIGH and lightOn == 0:
        lightOn = 1
        GPIO.output(4,GPIO.HIGH)
        time.sleep(1.0)
    if GPIO.input(btn1) == GPIO.HIGH and lightOn == 1:
        lightOn = 0
        GPIO.output(4,GPIO.LOW)
        time.sleep(1.0)
        
    # Mode Selection (btn2) for speed, acceleration, directions
    if GPIO.input(btn2) == GPIO.HIGH:
        stats += 1
        stats %= 3
        display_title(stats)

    dist = distance()
    if dist < dist_limit:
        lcd.clear()
        lcd.set_cursor(0,0)
        lcd.message("WARNING! Object \n behind: " "%.1f m" %int(dist))
        GPIO.output(4,GPIO.HIGH)
        time.sleep(1.0)
        display_title(stats)
    else:
        if  stats == 0:
            display_value("%.1f m/s" %int(vf))
        if  stats == 1:
            display_value("%.1f m/s^2" %int(accel_mag))
        if  stats == 2:
            display_value("LEFT 300m") #example of directions from Google API (feature in development)
    
# REFERENCES
# Accelerometer: https://pimylifeup.com/raspberry-pi-accelerometer-adxl345/
# Button: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
# Ultrasonic Sensor: https://pimylifeup.com/raspberry-pi-distance-sensor/
# 16x2 LCD: https://github.com/adafruit/Adafruit_Python_CharLCD
# Accelerometer: https://www.engineersgarage.com/raspberrypi/adxl345-accelerometer-raspberry-pi-i2c/
