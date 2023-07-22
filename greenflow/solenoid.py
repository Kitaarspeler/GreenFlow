import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


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
    turn_on()
        Turns the solenoid on
    turn_off()
        Turns the solenoid off
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

    def __str__(self):
        """Returns f string giving GPIO pin number and solenoid state

        """

        return f"GPIO pin: {self.pin}, State: {self.state}"

    @property
    def pin(self):
        """Get or set the GPIO pin number. Setting the pin will configure the 
        GPIO pin as an output automatically
        """
        
        return self._pin
    
    @pin.setter
    def pin(self, pin):
        if pin not in range(2, 28): # 2 to 27
            raise ValueError("GPIO pin not valid")
        else:
            self._pin = pin
            GPIO.setup(self._pin, GPIO.OUT)


    def turn_on(self):
        """Turns the solenoid on

        Also sets the solenoid state to True
        """
        
        self.state = True
        GPIO.output(self.pin, True)


    def turn_off(self):
        """Turns the solenoid off

        Also sets the solenoid state to False
        """
        
        self.state = False
        GPIO.output(self.pin, False)

