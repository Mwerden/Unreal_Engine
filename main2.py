# This is the main function of the code to run the tests. It runs 6 test for each graphical setting and then runs all the graphical settings (should be 52 different presets)
# There is a Thread that detects the launch of the game and then once the game is detected, the thread launches the other threads to start the prolfing tools.
# After the test finishes a seperate thread is used to analyzie and convert the gatord data to a csv.
# TODO: We changed the collection of Temperature for the UNity Boat Attack test. WE need to just use that function/file to use. Additionally this code has never best compiled since changing the pull data for suntemple and adding the thread to analzie the gatord data.
import BatchFile_GPU
# import re Not used right now

from perfettocollection import perfettoPowerData
import subprocess
import time
import threading
import os  # FIX: added so Windows can remove files without using rm

from getTemps2 import getTemps

from gatordCollection import gatordDataCOllection, prepareGatord
from setFrequency import createFreqFile
from graphicalSettings import generatePresets, updateGameSettingini
from pullDataSunTemple2 import pullData
from generate_events_config import generateConfig

FILE_SUFFIX = 5


# Create Function to detect when application is opened
def DetectLaunch(event):
    print("Running Logcat")
    subprocess.run('adb logcat -c', shell=True)
    log = subprocess.Popen(
        ['adb', 'logcat', 'ActivityManager:I', '*:S'],
        # adb logcat ActivityManager:I *:S - prints info level from ActivityManager
        stdout=subprocess.PIPE,
        text=True
    )

    # Look for line opening application
    try:
        for line in log.stdout:
            if "com.YourCompany.SunTemple2" in line and "Start proc" in line:
                print(f"Matched line: {line}")
                event.set()
                print("Event has been set")
                break
    finally:
        log.terminate()


def chooseTestsToRun(graphicalPresets, selection):
    # If user types "all" → run everything
    if selection == "all":
        return list(range(len(graphicalPresets)))

    # Otherwise assume it's a list of test numbers
    elif isinstance(selection, list):
        return selection

    else:
        print("Invalid selection, defaulting to all")
        return list(range(len(graphicalPresets)))


def main():
    graphicalPresets = generatePresets()

    # THIS IS THE ONLY LINE YOU CHANGE WHEN RUNNING TESTS

    # OPTION 1: run everything testSelection = "all"

    testSelection = "all"

    # OPTION 2: run specific tests (example: resolution 25 and 100)
    # testSelection = [5, 4]

    testToRun = chooseTestsToRun(graphicalPresets, testSelection)

    print("Test Being Run:")
    for t in testToRun:
        print(f"Test {t}: {graphicalPresets[t]}")

    for test in testToRun:

        # for test in range(NUMBER_OF_TEST_RUNS):

        print(f"Starting Up test number {test} at time {time.ctime(time.time())}")

        # If the file exists remove it
        try:
            # FIX: replaced Linux rm command with Python file removal so it works on Windows
            file_path = f"../../testData/sortedOutput{test}.csv"
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            print("Creating new data file!\n")

        paramDict = BatchFile_GPU.makeParamDict()

        duration = int(paramDict["DURATION"][0])

        updateGameSettingini(graphicalPresets[
                                 test])  # Pulls the updateGameSetting.ini in phone and updates it with the graphical setting and sends it back to phone

        for currentTestNo in range(0, len(paramDict["TESTS"][:]), 2):
            print("RUN", (currentTestNo // 2) + 1, "of", len(paramDict["TESTS"][1:]) // 2 + 1)
            BatchFile_GPU.makeBatchFile(paramDict, currentTestNo, test)

            startTime = time.time()

            # Create Event for application being opened
            startEvent = threading.Event()

            # subprocess.run("taskkill /F /IM adb.exe", shell=True)

            # Create thread to detect when the application is opened
            print("Creating DetectLaunch thread")
            detectThread = threading.Thread(target=DetectLaunch, args=(startEvent,))
            detectThread.start()
            print("DetectLaunch thread started")

            # create a thread so that the power recording process can run parallel to simpleperf.
            # First argument is the duration of the recording procces. Second is the interval specifying how often it is measured

            tempThread = threading.Thread(
                target=getTemps,
                args=(duration, 500, test, startEvent, currentTestNo, graphicalPresets[test])
            )

            CPU_counters = [
                "instructions",
                "branch-misses",
                "raw-l1d-cache",
                "raw-l1d-cache-refill"
            ]

            generateConfig(CPU_counters)

            perfettoPowerThread = threading.Thread(target=perfettoPowerData, args=(duration, startEvent))
            gatordThread = threading.Thread(target=gatordDataCOllection, args=(duration, startEvent))

            prepareGatord(paramDict, currentTestNo)

            print("Starting Perfetto and power thread")

            perfettoPowerThread.start()
            tempThread.start()
            gatordThread.start()

            # Creates the frequency .sh batch file and runs it
            createFreqFile()

            # FIX: chmod does not exist on Windows so it was removed
            # subprocess.run("chmod +x lock_freq.sh", shell=True)

            # FIX: run shell script through bash so it works on Windows if Git Bash or WSL is installed
            subprocess.run("bash lock_freq.sh", shell=True)
            print("Frequency Lock")

            # Run the batch file

            # Open Application
            subprocess.run(
                "adb shell su -c am start -n com.YourCompany.SunTemple2/com.epicgames.unreal.SplashActivity",
                shell=True
            )

            time.sleep(1)

            time.sleep(duration + 10)

            # Kill the process
            subprocess.run("adb shell su -c am force-stop com.YourCompany.SunTemple2", shell=True)

            time.sleep(5)

            # Wait for all collection threads to fully finish before pulling data
            detectThread.join()
            tempThread.join()
            perfettoPowerThread.join()
            gatordThread.join()

            # Pull data only after Gatord, Perfetto, and Temps are done
            pullData(test, currentTestNo, graphicalPresets[test])

            # Screenshot setup on phone, takes it on phone than pulls it
            subprocess.run("adb shell screencap -p /sdcard/screen.png", shell=True)

            # FIX: explicitly pull screenshot to testData folder
            subprocess.run(
                r"adb pull /sdcard/screen.png C:\Users\myd3192\Desktop\Unreal_Engine_ST2\testData",
                shell=True
            )

            # Stop game between runs
            subprocess.run(
                "adb shell su -c am force-stop com.YourCompany.SunTemple2",
                shell=True
            )

            # Kill old gatord process if still running
            subprocess.run(
                'adb shell su -c "pkill gatord"',
                shell=True
            )

            # Remove old remote APC after data was already pulled/saved
            subprocess.run(
                'adb shell su -c "rm -rf /data/local/tmp/outputGatord.apc"',
                shell=True
            )

            endTime = time.time()

            timeDifference = endTime - startTime
            print(f"Time done {time.ctime(time.time())}")
            print("Test took", timeDifference, "seconds!")

            # Allow for phone to cool
            time.sleep(20)


if __name__ == "__main__":
    main() 