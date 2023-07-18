#!/usr/bin/env python


import RPi.GPIO as GPIO


class Solenoid():
    """
    A class used to control a solenoid

    ...

    Attributes
    ----------
    pin : int
        a numbered GPIO pin used to interact with the solenoid
    state : bool
        the state of the solenoid (default is False, aka off)

    Methods
    -------
    toggle()
        Toggles the state of the solenoid e.g. turns on if off and vice versa
    """

    def __init__(self, pin, state=False):
        """
        Parameters
        ----------
        pin : int
            the GPIO pin used to interact with the solenoid
        state : bool
            the state of the solenoid (default is False, aka off)
        """

        self.pin = pin
        self.state = state

    @property
    def pin(self):
        """Get or set the GPIO pin number. Setting the pin will configure the 
        GPIO pin as an output automatically.
        """
        return self._pin
    
    @pin.setter
    def pin(self, pin):
        if pin not in range(1, 28): # 1 to 27
            raise ValueError("GPIO pin not valid")
        else:
            self._pin = pin
            GPIO.setup(self._pin, GPIO.OUT)


    def toggle(self):
        """Toggles the state of the solenoid e.g. turns on if off and vice versa

        Swaps the solenoid state and sets GPIO output to new state
        """
        
        self.state = not self.state
        GPIO.output(self.pin, self.state)

