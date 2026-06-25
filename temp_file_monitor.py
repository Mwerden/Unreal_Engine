import subprocess
import csv
import time

def temp_file_monitor(testDuration, startEvent, temp_interval):
    #Remove pervious temp file
    subprocess.run("adb shell su -c 'rm /data/local/tmp/temps.csv'", shell = True)
    startEvent.wait()
    print(f"Starting temp_file_monitor at {time.time()}")
    subprocess.run(f'''adb shell su -c 'taskset 002 "/data/local/tmp/temp_file_monitor {temp_interval} {testDuration}"' ''', shell=True, check=True)

