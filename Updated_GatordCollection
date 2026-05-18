# This files pulls the SunTemple2 files needed. I first pull the screeenshots, then pulls the Gatord apc file, perfetto data, pulls the GameUserSEttings.ini file, it also pulls the Monotonic frame timestamps csv as well
# After it renames all of them and moves them to the test data directory.
import subprocess
import os
from graphicalPresets import get_setting_folder
import shutil


def pullData(test, currentTestNo, preset):
    folder = get_setting_folder(preset)
    if folder is None:
        print(f"Skipping test {test}: not a valid baseline or single-setting test.")
        return  # Skip this test

    output_dir = os.path.join("../../testData/SunTemple2-2025-07-11/TestData-2026", folder)
    os.makedirs(output_dir, exist_ok=True)

    screenShotDir = "/sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Screenshots/Android/"
    outputDir = f".../../testData/SunTemple2-2025-07-11/TestData-2026/screenshots/test{test}_run{currentTestNo}"
    os.makedirs(outputDir, exist_ok=True)

    print(f"Pulling all screenshots from {screenShotDir} to {outputDir}")

    # Pull entire screenshot folder contents to local_output_dir
    subprocess.run("adb pull " + screenShotDir + " " + outputDir, shell=True)

    # Delete all screenshots (.png files) on the device
    subprocess.run(f'adb shell su -c "rm {screenShotDir}*.png"', shell=True)
    print(f"Successfully pulled and deleted screenshots for test {test}, run {currentTestNo}")

    # Pull apc file
    subprocess.run("adb pull /data/local/tmp/outputGatord.apc", shell=True)
    # Pull monotonic time
    subprocess.run("adb pull /data/local/tmp/monotonic_start.txt", shell=True)
    # Pull GameUserSettings.ini
    subprocess.run(
        "adb pull /sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Config/Android/GameUserSettings.ini GameUserSettings.ini",
        shell=True, check=True)
    # Pull Monotonic Frame Time from Game
    subprocess.run("adb pull /sdcard/Android/data/com.YourCompany.SunTemple2/filesmonotonic_log.csv", shell=True)

    # Generate GPU CSV using APC file
    cli_path = r"C:\Program Files\Arm\Arm Performance Studio 2026.1\streamline\Streamline-cli.exe"

    apc_path = r"C:\Users\Micah\Desktop\2026 Unreal Research\SunTemple2Script2025\SunTemple2Script2025\outputGatord.apc"

    output_dir = r"C:\Users\Micah\Desktop\2026 Unreal Research\SunTemple2Script2025\SunTemple2Script2025\testData"

    subprocess.run(
        f'"{cli_path}" -report "{apc_path}" -format csv -output "{output_dir}"',
        shell=True,
        check=True)

    # Rename CSV files based on test and run number
    # Copy files (Python-native, cross-platform)
    Output_Gatord_dir = os.path.join(output_dir, "Out_Gatord", folder)
    os.makedirs(Output_Gatord_dir, exist_ok=True)
    shutil.copy(
        "timeline.csv",
        os.path.join(output_dir, "outputGatord.csv")
    )
    perfetto_data_dir = os.path.join(output_dir, "Perfetto_Data", folder)
    os.makedirs(perfetto_data_dir, exist_ok=True)
    shutil.copy(
        "test_draft_perfetto.csv",
        os.path.join(output_dir, f"perfettoData_test{test}_{currentTestNo // 2}.csv")
    )
    gator_ref_dir = os.path.join(output_dir, "GatorRef", folder)
    os.makedirs(gator_ref_dir, exist_ok=True)
    shutil.copy(
        "monotonic_start.txt",
        os.path.join(output_dir, f"gator_reference_time_test{test}_{currentTestNo // 2}.txt")
    )

    Mono_dir = os.path.join(output_dir, "MonotonicFrames", folder)
    os.makedirs(Mono_dir, exist_ok=True)
    shutil.copy(
        "filesmonotonic_log.csv",
        os.path.join(Mono_dir, f"monotonicFramesTime_test{test}_{currentTestNo // 2}.csv")
    )

    game_settings_dir = os.path.join(output_dir, "GameSettings", folder)
    os.makedirs(game_settings_dir, exist_ok=True)
    shutil.copy(
        "GameUserSettings.ini",
        os.path.join(game_settings_dir, f"GameUserSettings_test{test}_{currentTestNo // 2}.ini")
    )
    # Delete local files (cross-platform)
    if os.path.exists("outputGatord.apc"):
        shutil.rmtree("outputGatord.apc", ignore_errors=True)

    for file in [
        "monotonic_start.txt",
        "GameUserSettings.ini",
        "filesmonotonic_log.csv",
        "test_draft_perfetto.csv",
        "outputGatord.csv"
    ]:
        if os.path.exists(file):
            os.remove(file)
