#!/bin/bash

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu1/cpufreq/scaling_min_freq"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu1/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu2/cpufreq/scaling_min_freq"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu2/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu3/cpufreq/scaling_min_freq"
adb shell su -c "echo 1197000 > /sys/devices/system/cpu/cpu3/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu4/cpufreq/scaling_min_freq"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu4/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu5/cpufreq/scaling_governor"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu5/cpufreq/scaling_min_freq"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu5/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu6/cpufreq/scaling_governor"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu6/cpufreq/scaling_min_freq"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu6/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu7/cpufreq/scaling_governor"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu7/cpufreq/scaling_min_freq"
adb shell su -c "echo 1945000 > /sys/devices/system/cpu/cpu7/cpufreq/scaling_max_freq"

adb shell su -c "echo userspace > /sys/devices/system/cpu/cpu8/cpufreq/scaling_governor"
adb shell su -c "echo 2556000 > /sys/devices/system/cpu/cpu8/cpufreq/scaling_min_freq"
adb shell su -c "echo 2556000 > /sys/devices/system/cpu/cpu8/cpufreq/scaling_max_freq"

echo "CPU frequency governors and limits set to userspace"

