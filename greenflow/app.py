#!/usr/bin/env python


import sys
import RPi.GPIO as GPIO
from solenoid import Solenoid
from flask import Flask, render_template


app = Flask(__name__)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


    try:
        solenoid1 = Solenoid(4, False)
    except ValueError:
        sys.exit("GPIO pin number not valid")

    GPIO.cleanup()


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()