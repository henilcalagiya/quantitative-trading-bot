import sched
import time
import subprocess
import pytz
from datetime import datetime, timedelta

def run_script(script):
    # Runs a Python script in a new terminal and returns the process
    process = subprocess.Popen(['gnome-terminal', '--', 'python', script])
    return process

def terminate_script(process, script):
    # Terminate the given process
    process.terminate()
    print(f"Terminated {script}")

def schedule_task(scheduler, time_to_run, script, is_termination=False, process=None):
    # Calculate the delay needed from now till the scheduled time
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    delay = (time_to_run - now).total_seconds()
    if delay < 0:
        print(f"Time for {script} has already passed.")
        return  # Time has passed, do not schedule
    if is_termination:
        print(f"Scheduling termination of {script} at {time_to_run}")
        scheduler.enter(delay, 1, terminate_script, argument=(process, script))
    else:
        print(f"Scheduling {script} to run at {time_to_run}")
        process = scheduler.enter(delay, 1, run_script, argument=(script,))
        return process

def main():
    scheduler = sched.scheduler(time.time, time.sleep)
    ist_zone = pytz.timezone('Asia/Kolkata')

    # Define the times you want to run your scripts in IST
    today = datetime.now(ist_zone)
    time_for_task1_start = ist_zone.localize(datetime(today.year, today.month, today.day, 9, 13))
    time_for_task1_stop = ist_zone.localize(datetime(today.year, today.month, today.day, 15, 30))
    time_for_task2_start = ist_zone.localize(datetime(today.year, today.month, today.day, 9, 15))
    time_for_task2_stop = ist_zone.localize(datetime(today.year, today.month, today.day, 15, 20))

    # Schedule the tasks to start
    process1 = schedule_task(scheduler, time_for_task1_start, '1fetch_tick_data_live.py')
    process2 = schedule_task(scheduler, time_for_task2_start, 'process_live_data.py')

    # Schedule the tasks to stop
    schedule_task(scheduler, time_for_task1_stop, '1fetch_tick_data_live.py', True, process1)
    schedule_task(scheduler, time_for_task2_stop, 'process_live_data.py', True, process2)

    # Run the scheduler
    scheduler.run()

if __name__ == "__main__":
    main()