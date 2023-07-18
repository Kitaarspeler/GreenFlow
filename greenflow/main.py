#!/usr/bin/env python


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid


def main():
    GPIO.setmode(GPIO.BCM)
    try:
        solenoid1 = Solenoid(11, False)
    except ValueError:
        sys.exit("GPIO pin number not valid")

if __name__ == "__main__":
    main()