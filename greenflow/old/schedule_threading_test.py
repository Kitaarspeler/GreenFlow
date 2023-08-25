from datetime import datetime
import threading
import time
import sys

import schedule


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. 
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
                
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def background_job(id):
    print(f"{id}: {datetime.now().isoformat()}")

count = 1

try:
    schedule.every().second.do(background_job, count)

    # Start the background thread
    stop_run_continuously = run_continuously()

    while True:
        if input("") == "y":
            count += 1
            schedule.every().second.do(background_job, count) 

    # Do some other things...
    print("Printing...")
    time.sleep(10)

    # Stop the background thread
    stop_run_continuously.set()
except KeyboardInterrupt:
    #stop_run_continuously.set()
    sys.exit()

