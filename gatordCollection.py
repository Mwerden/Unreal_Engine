# This is the code for setting up gatord for our tests. We prepareGator by generating the config file by called generateConfig() function from the Generate_Config file
# and pushing it to the phone. We also remove the previous gatord output file.
# This code also has the gatordDataCollection function which runs gatord on the phone when the Event is set and pulls the output file to the computer.

import subprocess
import Generate_config as gc
import csv
import time


def wait_for_apc_files(timeout=40):
    # Wait until Gatord fully writes the APC folder before pullData tries to pull it
    needed = ["0000000000", "captured.xml", "counters.xml", "events.xml"]
    start = time.time()

    while time.time() - start < timeout:
        result = subprocess.run(
            'adb shell su -c "ls /data/local/tmp/outputGatord.apc"',
            shell=True,
            capture_output=True,
            text=True
        )

        files = result.stdout

        if all(file in files for file in needed):
            print("Gatord APC complete")
            return True

        print("Waiting for full Gatord APC...")
        print(files)
        time.sleep(2)

    print("ERROR: Gatord APC never completed")
    print(files)
    return False


def gatordDataCOllection(testDuration, startEvent):
    startEvent.wait()
    # barrier.wait()

    # Kill any old Gatord process before starting a new run
    subprocess.run(
        'adb shell su -c "pkill gatord"',
        shell=True
    )

    time.sleep(2)

    # Remove pervious Gatord output directory
    subprocess.run(
        'adb shell su -c "rm -rf /data/local/tmp/outputGatord.apc"',
        shell=True
    )

    time.sleep(1)

    result = subprocess.run(
        "adb shell su -c \"taskset 020 /data/local/tmp/gatord "
        "-c /data/local/tmp/configuration.xml "
        "-o /data/local/tmp/outputGatord "
        "-l com.YourCompany.SunTemple2 "
        "-t " + str(testDuration) + " "
        "--append-events-xml /data/local/tmp/events-Cortex-X3.xml "
        "--append-events-xml /data/local/tmp/events-Cortex-A715.xml "
        "--append-events-xml /data/local/tmp/events-Cortex-A510.xml "
        "--sample-rate low\"",
        shell=True
    )  # Shell has to be shell case-sensitive

    print("Gatord finished with return code:", result.returncode)

    # Give Gatord time to finish closing the APC folder
    time.sleep(5)  # windows cmd version for sleep

    # Check that Gatord made the full APC before pullData runs
    wait_for_apc_files()

    print("Remote Gatord APC files:")
    subprocess.run(
        'adb shell su -c "ls -l /data/local/tmp/outputGatord.apc"',
        shell=True
    )

    # APC file is now pulled in pullDataSunTemple2.py
    # subprocess.run("adb pull /data/local/tmp/outputGatord.apc\n\n", shell=True)  # Case-sensitve here too


# create dictionary with in case get rid of BatchfIle.
def makeParamDict():
    # Create variables for each parameter
    paramDict = {}

    # Open parameters and collect the values of the different parameters

    with open('parameters2.csv', 'r') as f:
        params = list(csv.reader(f))
        for row in params:
            paramDict.update({row[0]: row[1:]})
        return paramDict


def prepareGatord(paramDict, currentTestNo):
    testList = [cleanNames(test) for test in paramDict['TESTS'][currentTestNo:currentTestNo + 2]]
    gc.generateConfig(testList)

    # Push config file to phone
    subprocess.run("adb push configuration.xml /data/local/tmp", shell=True)

    # Remove pervious Gatord output directory
    subprocess.run('adb shell su -c "rm -rf /data/local/tmp/outputGatord.apc"', shell=True)


def cleanNames(key):
    key = str(key)
    key = key.translate({ord(i): None for i in "[] '"})
    return key