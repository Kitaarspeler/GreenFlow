#!/usr/bin/env python


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid
from time import sleep


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    try:
        solenoid1 = Solenoid(4, False)
    except ValueError:
        sys.exit("GPIO pin number not valid")

    solenoid1.toggle()
    sleep(5)
    solenoid1.toggle()

if __name__ == "__main__":
    main()