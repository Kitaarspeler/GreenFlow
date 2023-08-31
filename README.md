# GreenFlow
RPi Garden Watering Automation System

## Classes
* Users [SQLAlchemy]
* Solenoids [SQLAlchemy]
* Interface [Flask]
* Schedules (not yet implemented)

## To Do
* Check weather patterns
    * If no precipitation forecast:
        * Water at best time (google it)
        * Length of time related to heat of day
* Opt in/out to weather auto-water for each zone
* Give index watering option of specific time to water for
* Set up schedule database
* Enter current password to change user details (plus fresh cookie validation?)
* Set up initial set up page to get solenoids and info