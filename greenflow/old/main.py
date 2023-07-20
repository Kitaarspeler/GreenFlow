#!/usr/bin/env python


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    try:
        solenoid1 = Solenoid(4, False)
    except ValueError:
        sys.exit("GPIO pin number not valid")

    GPIO.cleanup()





if __name__ == "__main__":
    main()