#This generates the configuration file needed for test seperate test for profiling with gatord. 
# An important note is that raw-l3d-cache-refill is not an event tath gatord can collect on the Cortex-A510.
#If in the future you want to add more metrics or different PMU to the configuration, you can either get the needed Lookup Table information by 
# Going on Streamline GUI 
def generateConfig(CPU_counters):

    #Use the CPU name in parameters to define the requried synatax for the configuration file
    LookupTable_x3 = {
        "instructions": 'event="0x8',
        "branch-misses": 'event="0x10',
        "raw-l1d-cache": 'event="0x4',
        "raw-l1d-cache-refill": 'event="0x3',
        "raw-l1i-cache": 'event="0x14',
        "raw-l1i-cache-refill": 'event="0x1',
        "raw-l2d-cache": 'event="0x16',
        "raw-l2d-cache-refill": 'event="0x17',
        "raw-l3d-cache": 'event="0x2b',
        "raw-l3d-cache-refill": 'event="0x2a',
        "raw-mem-access": 'event="0x13'
    }
    LookupTable_A510 = {
        "instructions": 'event="0x8',
        "branch-misses": 'event="0x10',
        "raw-l1d-cache": 'event="0x4',
        "raw-l1d-cache-refill": 'event="0x3',
        "raw-l1i-cache": 'event="0x14',
        "raw-l1i-cache-refill": 'event="0x1',
        "raw-l2d-cache": 'event="0x16',
        "raw-l2d-cache-refill": 'event="0x17',
        "raw-l3d-cache": 'event="0x2b',
        "raw-l3d-cache-refill": None, #This does not exist on the A510
        "raw-mem-access": 'event="0x13'
    }
    LookupTable_A715 = {
        "instructions": 'event="0x8',
        "branch-misses": 'event="0x10',
        "raw-l1d-cache": 'event="0x4',
        "raw-l1d-cache-refill": 'event="0x3',
        "raw-l1i-cache": 'event="0x14',
        "raw-l1i-cache-refill": 'event="0x1',
        "raw-l2d-cache": 'event="0x16',
        "raw-l2d-cache-refill": 'event="0x17',
        "raw-l3d-cache": 'event="0x2b',
        "raw-l3d-cache-refill": 'event="0x2a',
        "raw-mem-access": 'event="0x13'
    }
    #Currently hardcoded need to do a study to ensure we have enough GPU performance counters
    GPU_counters = [
        '<configuration counter="ARM_Mali-G715_GPU_ITER_ACTIVE"/>',
        #'<configuration counter="ARM_Mali-G715_CALL_BLEND_SHADER"/>', Does not give data. Maybe no Shader instructions
        '<configuration counter="ARM_Mali-G715_L2_READ_LOOKUP"/>',
        '<configuration counter="ARM_Mali-G715_L2_EXT_WRITE"/>',
        '<configuration counter="ARM_Mali-G715_L2_WRITE_LOOKUP"/>',
        '<configuration counter="ARM_Mali-G715_L2_EXT_READ"/>',
        '<configuration counter="ARM_Mali-G715_L2_EXT_WRITE_BEATS"/>',
        '<configuration counter="ARM_Mali-G715_L2_EXT_READ_BEATS"/>',
    ]

    with open("configuration.xml", "w") as f:

        #Write Headers
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<configurations revision="3" gpu_public_name="Mali-G715" streamline_version="960">\n')

        # Write GPU counters
        for GPU_config in GPU_counters:
            f.write(f'    {GPU_config}\n')

        #Always Track CPU cycles with ccnt counter for cortex or cnt0 for A510 and A715
        f.write('    <configuration counter="ARMv9_Cortex_X3_ccnt" event="0x11"/>\n')
        f.write('    <configuration counter="ARMv9_Cortex_A715_cnt0" event="0x11"/>\n')
        f.write('    <configuration counter="ARMv8_Cortex_A510_cnt0" event="0x11"/>\n')

        #Write to config if parameter matches
        for i in range(len(CPU_counters)):
            counter_name = CPU_counters[i].replace("'", "")

            CPUConfig = LookupTable_x3.get(counter_name)
            if CPUConfig is not None and "None" not in CPUConfig:
                f.write(f'    <configuration counter="ARMv9_Cortex_X3_cnt{i}" {CPUConfig}"/>\n')

            CPUConfig = LookupTable_A715.get(counter_name)
            if CPUConfig is not None and "None" not in CPUConfig:
                f.write(f'    <configuration counter="ARMv9_Cortex_A715_cnt{i+1}" {CPUConfig}"/>\n')

            CPUConfig = LookupTable_A510.get(counter_name)
            if CPUConfig is not None and "None" not in CPUConfig:
                f.write(f'    <configuration counter="ARMv8_Cortex_A510_cnt{i+1}" {CPUConfig}"/>\n')

        #Close XML
        f.write('</configurations>\n')