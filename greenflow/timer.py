#!/usr/bin/env python


import schedule
import time



class Timer():
    """
    A class used to set a timer

    ...

    Attributes
    ----------
    length : int
        the length of the timer in minutes

    Methods
    -------
    
    """

    def __init__(self, length):
        """
        Parameters
        ----------
        length : int
            the length of the timer in minutes
        """

        self.length = length

    @property
    def length(self):
        """Get or set the length of the timer in minutes. If length is lower
        than one, a ValueError is raised
        """

        return self._length
    
    @length.setter
    def length(self, length):
        if length < 1:
            raise ValueError("Timer is too short")
        else:
            self._length = length


    def toggle(self):
        """Toggles the state of the solenoid e.g. turns on if off and vice versa

        Swaps the solenoid state and sets GPIO output to the new state
        """
        