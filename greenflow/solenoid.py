#!/usr/bin/env python

class Solenoid():
    """
    A class used to control a solenoid

    ...

    Attributes
    ----------
    pin : int
        the GPIO pin used to interact with the solenoid
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

    
