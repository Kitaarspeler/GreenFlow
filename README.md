# GreenFlow
RPi Garden Watering Automation System

## Classes
* Users [SQLAlchemy]
* Solenoids [SQLAlchemy]
* Interface [Flask]
* Schedules (not yet implemented)

## To Do
* Rewrite routes to use /settings/del or /settings/add etc
* Enter current password to change user details (plus fresh cookie validation?)
* Set up initial set up page to get solenoids and info
* Can't turn on solenoid with no timer, needs to have timer set so doesn't run indefinitely
* Schedule page