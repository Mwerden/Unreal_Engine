This folder contains the code for running the SunTemple Script.
Each file also has a comment at the top telling what each file code does

A couple of important notes. Due to time constraints we switched our benchmark testing to do Unity around 3 weeks to go before our REU ended. As a result, we were not able to test with this SunTemple2 Script. I changed the code but was not able to test and debug so there most likely will be some slight errors. Additionally, since we went with unity, there were some changes we made to the unity script. These are different collection methods for temperature and also how we generate the config file for gatord. These files are listed in the "Need to Integrate into Main Script" directory and is the code we used for Unity.

Files in the directory:

gatordCollection: 
This is the code for setting up gatord for our tests. We prepareGator by generating the config file by called generateConfig() function from the Generate_Config file and pushing it to the phone. We also remove the previous gatord output file. This code also has the gatordDataCollection function which runs gatord on the phone when the Event is set and pulls the output file to the computer.


Generate_config: 
This generates the configuration file needed for test seperate test for profiling with gatord. An important note is that raw-l3d-cache-refill is not an event tath gatord can collect on the Cortex-A510. If in the future you want to add more metrics or different PMU to the configuration, you can either get the needed Lookup Table information by Going on Streamline GUI 

getTemps: Old collection of data for temperature by reading teh temp zones on the phone. TODO: Intergrate new method similar to Unity

graphicalSettings: Code to generate teh different presets for graphical settings and to update and push teh graphical settings

graphicaPresets:
This file has a function that will read the preset list, and figure out which setting is on and which setting is getting changed Such as ShadowQualityLow. THis will be used for organizing the data and naming the directories.
Not tested yet.

