import csv
import os

LENGTH_OF_FIRST_TEST = 0
LENGTH_OF_NTH_TEST = 90
CPU_CORE = 8
PROGRAM_THREAD_NAME = "u0_a304"


def main():
    paramDict = makeParamDict()
    makeBatchFile(paramDict, 0, 0)



# Load parameters from CSV

def makeParamDict():

    paramDict = {}

    with open('parameters2.csv', 'r') as f:
        params = list(csv.reader(f))

        for row in params:
            paramDict[row[0]] = row[1:]

    return paramDict



# Generate simpleperf batch file

def makeBatchFile(paramDict, currentTestNo, runNum):

    os.makedirs("../simplePerfFiles", exist_ok=True)
    os.makedirs("../testData/simpleperf", exist_ok=True)
    os.makedirs("../testData/screenshots", exist_ok=True)

    scriptPath = "../simplePerfFiles/simplePerf.bat"

    with open(scriptPath, 'w') as f:

        loopsOrDur = cleanNames(paramDict['LOOPSorDURATION'][0]).strip().upper()

        # Determine duration / loops
        if loopsOrDur == 'DURATION':

            testDuration = int(cleanNames(paramDict['DURATION'][0]))
            loopsNo = testDuration // (LENGTH_OF_FIRST_TEST + LENGTH_OF_NTH_TEST)

        elif loopsOrDur == 'LOOPS':

            loopsNo = int(cleanNames(paramDict['LOOPS'][0]))
            testDuration = loopsNo * LENGTH_OF_NTH_TEST + LENGTH_OF_FIRST_TEST


        else:
            raise ValueError("Invalid LOOPSorDURATION parameter")


        # Select 3 events from test list
        testList = paramDict['TESTS'][currentTestNo:currentTestNo + 3]

        # Convert list to comma separated events
        eventList = ",".join([cleanNames(x) for x in testList])

        outputFile = f"simpleperf_test{runNum}_run{currentTestNo//2}.csv"


        # Write shell script


        f.write("@echo off\n\n") # setting to windows compat no linux

        f.write("echo 'Starting SimplePerf collection'\n\n")

        # Launch application
        f.write(
            f"adb shell su -c am start -n {cleanNames(paramDict['APPLICATION'][0])}\n\n"
        )

        # Get PID
        # TODO if I use this I need to change to windows commands
        # f.write(
        #     f"pid=$(adb shell ps | grep {PROGRAM_THREAD_NAME} | awk 'NR==1 {{print $2}}')\n\n"
        # )
        #
        # # Pin process to CPU core
        # f.write(
        #     f"adb shell su -c taskset -p {cleanNames(paramDict['CPU_CORE'])} $pid\n\n"
        # ) this is linux based



        # Run simpleperf
        f.write(
            "adb shell su -c \"simpleperf stat "
            f"-e {eventList} "
            f"--app {cleanNames(paramDict['APPLICATION'][0]).split('/',1)[0]} "
            f"--cpu {CPU_CORE} "
            f"--duration {testDuration} "
            f"--interval {cleanNames(paramDict['INTERVAL'][0])} "
            f"--csv "
            f"-o /data/local/tmp/{outputFile}\" \n\n"
        )

        # Move CSV to public storage
        f.write(
            f"adb shell su -c cp /data/local/tmp/{outputFile} /sdcard/{outputFile}\n\n"
        )

        # Pull CSV to host
        f.write(
            f"adb pull /sdcard/{outputFile} ../testData/simpleperf/{outputFile}\n\n"
        )

        # Screenshot Collection

        for i in range(loopsNo):
            for j in range(3):

                shot = f"ScreenShot{str(i*3 + j).zfill(5)}.png"

                f.write(
                    f"adb pull {cleanNames(paramDict['SCREENSHOT_PATH'])}{shot} "
                    f"../testData/screenshots/{shot}\n"
                )

                f.write(
                    f"adb shell su -c rm {cleanNames(paramDict['SCREENSHOT_PATH'])}{shot}\n\n"
                )

        # ----------------------------
        # FPS Chart Stats (first test only)
        # ----------------------------

        if currentTestNo == 0:

            f.write("echo 'Collecting FPS stats'\n\n")

            f.write("rmdir /S /Q FPSChartStats\n\n")

            f.write(
                "adb pull "
                "/sdcard/Android/data/com.YourCompany.SunTemple2/files/"
                "UnrealGame/SunTemple2/SunTemple2/Saved/Profiling/FPSChartStats\n\n"
            )

            f.write(
                f"move FPSChartStats ..\\testData\\FPSChartStats{runNum}\n\n"
            )

    # Make script executable
    # os.chmod(scriptPath, 0o755)  this is only linux not windows needed

    print(f"Generated batch file: {scriptPath}")

# ---------------------------------------
# Clean list formatting# ---------------------------------------
def cleanNames(key):

    key = str(key)

    key = key.translate({ord(i): None for i in "[] '"})

    return key


# Uncomment for standalone test
# main()