# This code generates a bash file to be able to call adb sheel and set the CPU and GPU frequencies for the Google Pixel 8a.
# We set the CPU frequencies to be around the middle frequencies that the cores ca operate. You can find all the frequeinces each CPU core can
# Operate by reading the file that should be something like scaling_available_frequencies in the /sys/devices/system/cpu/cpu#/cpufreq/ directory.
# ISSUE!!!! When setting the GPU frequency, the game crashes. We are unsure why this is happening and need to investigate further.

def createFreqFile():
    cpu_cortex_A510 = 1197000
    cpu_cortex_A715 = 1945000
    cpu_cortex_X3 = 2556000
    gpu_freq = 749000
    with open("lock_freq.sh", 'w', newline="\n") as f:
        f.write("#!/bin/bash\n\n")

        # Code to set frequency for each of the cores
        for i in range(0, 9):
            if 3 >= i >= 0:
                freq = cpu_cortex_A510
            elif 4 <= i <= 7:
                freq = cpu_cortex_A715
            else:
                freq = cpu_cortex_X3
            f.write(f"adb shell su -c \"echo userspace > /sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor\"\n")
            f.write(f"adb shell su -c \"echo {freq} > /sys/devices/system/cpu/cpu{i}/cpufreq/scaling_min_freq\"\n")
            f.write(f"adb shell su -c \"echo {freq} > /sys/devices/system/cpu/cpu{i}/cpufreq/scaling_max_freq\"\n\n")

        f.write("echo \"CPU frequency governors and limits set to userspace\"\n\n")

        '''f.write("adb shell su -c \"echo basic > /sys/devices/platform/1f000000.mali/governor\"\n") #Sets the GPU governor
        f.write(f"adb shell su -c \"echo {gpu_freq} > /sys/devices/platform/1f000000.mali/scaling_min_freq\"\n")
        f.write(f"adb shell su -c \"echo {gpu_freq} > /sys/devices/platform/1f000000.mali/scaling_max_freq\"\n\n")
       
        f.write(f"echo \"GPU governor set to {gpu_freq}\"\n\n")'''


if __name__ == "__main__":
    createFreqFile()  # runs main
    print("Made file")
