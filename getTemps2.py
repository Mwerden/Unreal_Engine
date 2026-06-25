import pandas as pd
import subprocess
import time
import threading
import os
from graphicalPresets import get_setting_folder


FILE_PREFIX = "tempOutputs"
FILE_TYPE = ".csv"
THERMAL_ZONES = ("BIG", "MID", "LITTLE", "G3D", "soc_therm")
NUM_OF_ZONES = len(THERMAL_ZONES)


def getTemps(duration, interval, test, startEvent, currentTestNo, preset):
    # Wait until games has been opened to start data collection
    startEvent.wait()
    print(f"Starting Temps at {time.time()}")

    temps = []
    times = []

    numofRuns = int(duration // (interval / 1000))

    # Write 5 shell files to get different temps
    # for i in range(NUM_OF_ZONES):
    #     writeTempShell(i)
    # NEW: No shell scripts needed anymore (handled directly with adb)

    # Clear common output file

    startTime = time.time()
    runNumber = 0

    # Run shell file and extract necessary data
    while time.time() - startTime < duration:
        start = time.time()
        temp = []

        # Get temp data from phone

        tempThreads = []

        for i, zone in enumerate(THERMAL_ZONES):
            tempThreads.append(FileThread(target=runFiles, args=(zone,)))  # made tuple
            tempThreads[i].start()

        # Organize data into dictionary

        # print("test took:", end-start, "seconds")

        if runNumber > 0:
            times.append(interval / 1000 + times[runNumber - 1])
        else:
            times.append(interval / 1000)

        runNumber += 1

        for i in range(len(tempThreads)):
            tempThreads[i].join()
            temp.append(tempThreads[i].result)

        temps.append(temp)

        end = time.time()

        print(f"Test took {end - start} seconds.")

        if end - start < interval / 1000:
            time.sleep(interval / 1000 - (end - start))

    thermalList = []

    for temp in temps:
        for i in temp:
            # thermalList.append(i.strip("\n").split(": "))
            parts = i.strip().split(": ")

            if len(parts) == 2:
                thermalList.append(parts)
            # NEW: safer parsing to avoid crashes

    tempsFinal = {}

    for runNum in range(len(temps)):
        if runNum == 0:
            print(thermalList)
            tempsFinal = {key: [value] for key, value in thermalList[:5]}

        elif runNum > 0:
            for i, key in enumerate(tempsFinal.keys()):
                tempsFinal[key].append(thermalList[runNum * 5 + i][1])

    tempDF = pd.DataFrame(tempsFinal)

    # Write to csv
    tempDF.insert(0, "time (s)", times)
    tempDF.set_index("time (s)", inplace=True)

    # Get preset folder name
    folder = get_setting_folder(preset)

    # Fallback if preset folder is invalid
    if folder is None:
        folder = f"test{test}"

    # Base output directory
    base_output_dir = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\testData"

    # Create Temp_Data/<test_folder> directory
    temp_output_dir = os.path.join(
        base_output_dir,
        "Temp_Data",
        folder
    )

    os.makedirs(temp_output_dir, exist_ok=True)

    # Build csv filename
    filename = os.path.join(
        temp_output_dir,
        FILE_PREFIX + str(test) + "-" + str(currentTestNo // 2) + FILE_TYPE
    )

    # Save csv
    tempDF.to_csv(filename, sep=",", encoding="utf-8")

    # print(f"Temps Done at {time.ctime(time.time())}!")
    print(f"Saved temps to: {filename}")


def writeTempShell(component):
    filename = "getTemp" + str(THERMAL_ZONES[component]) + ".sh"

    with open(filename, "w") as f:
        # Shebang
        f.write("#!/bin/sh\n\n")

        # Get temp
        f.write("""temp=$(adb shell su -c "cat /sys/class/thermal/thermal_zone""" + str(component) + """/temp")\n\n""")

        # Write temp to outfile
        f.write("""echo " """ + str(THERMAL_ZONES[component]) + """: $((temp/1000))"\n\n""")

    # subprocess.run("chmod +x ./" + filename, shell=True)
    # NEW: Removed chmod (not supported on Windows)


def runFiles(component):
    # filename = "./getTemp" + str(component) + ".sh"
    # temp = subprocess.run(filename, shell=True, capture_output=True, text=True)
    # return temp.stdout

    # NEW: Direct adb call (no bash / .sh files)
    zone_index = THERMAL_ZONES.index(component)

    cmd = [
        "adb", "shell", "su", "-c",
        f"cat /sys/class/thermal/thermal_zone{zone_index}/temp"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return f"{component}: ERROR"

    try:
        temp_c = int(result.stdout.strip()) // 1000
        return f"{component}: {temp_c}"

    except:
        return f"{component}: INVALID"


class FileThread(threading.Thread):
    def __init__(self, target, args=()):
        # threading.Thread.__init__(self)
        super().__init__()

        self.target = target
        self.args = args

        # self.result = self.target(self.args)
        self.result = None  # was not running in thread before was reading simultanously

    def run(self):
        self.result = self.target(*self.args)


# getTemps(180, 500, 1)