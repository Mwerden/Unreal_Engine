# This is the code for setting up gatord for our tests. We prepareGator by generating the config file by called generateConfig() function from the Generate_Config file
# and pushing it to the phone. We also remove the previous gatord output file.  
# This code also has the gatordDataCollection function which runs gatord on the phone when the Event is set and pulls the output file to the computer.

import subprocess
import Generate_config as gc
import csv
import time


def gatordDataCOllection(testDuration, startEvent):
    startEvent.wait()
    # barrier.wait()
    subprocess.run(
        "adb shell su -c \"taskset 020 /data/local/tmp/gatord -c /data/local/tmp/configuration.xml -o /data/local/tmp/outputGatord -l com.YourCompany.SunTemple2 -t " + str(
            testDuration) + " --append-events-xml /data/local/tmp/events-Cortex-X3.xml --append-events-xml /data/local/tmp/events-Cortex-A715.xml --append-events-xml /data/local/tmp/events-Cortex-A510.xml --sample-rate low\" &\n\n",
        shell=True)  # Shell has to be shell case-sensitive
    # subprocess.run(f"sleep {int(testDuration) + 20}\n\n",
    #                shell=True)  # Sleep for the duration of the test plus a buffer
    time.sleep(testDuration + 20)  # windows cmd version for sleep
    subprocess.run("adb pull /data/local/tmp/outputGatord.apc\n\n", shell=True)  # Case-sensitve here too


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
    subprocess.run("adb shell su -c 'rm -r /data/local/tmp/outputGatord.apc'", shell=True)


def cleanNames(key):
    key = str(key)
    key = key.translate({ord(i): None for i in "[] '"})
    return key
