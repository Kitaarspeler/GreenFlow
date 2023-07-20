"""GreenFlow RPi based garden watering system

This program allows the user to set up multiple solenoids for turning
on and off multiple hoses to water different parts of their garden.
"""


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid
from flask import Flask, render_template


app = Flask(__name__)


def main():
    """Initialises GPIO pins, solenoids and schedules

    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    solenoids = {}

    num_solenoids = int(get_num_solenoids())
    for i in range(1, num_solenoids+1):
        try:
            solenoids[i] = Solenoid(i + 1, False)
        except ValueError:
            sys.exit("Too many solenoids. Re-run program with 27 or fewer solenoids")
    GPIO.cleanup()


def get_solenoids():
    """Gets and returns the number of solenoids needed for this install
    
    Returns
    -------
    int
        The number of solenoids needed for this implementation
    """

    num_solenoids = 0
    while True:
        if num_solenoids < 1 or num_solenoids > 27:
            num_solenoids = input("Please enter the number of solenoids needed for this install: ")
        else:
            break
    return num_solenoids


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    main()
    app.run(
        debug = True,
        host = "0.0.0.0",
        port = 80,
        )