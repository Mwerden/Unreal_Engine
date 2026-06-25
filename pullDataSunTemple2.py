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

    base_output_dir = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\testData"
    os.makedirs(base_output_dir, exist_ok=True)

    run_no = currentTestNo // 2

    screenShotDir = "/sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Screenshots/Android/"
    outputDir = os.path.join(base_output_dir, "screenshots", folder, f"test{test}_run{run_no}")
    os.makedirs(outputDir, exist_ok=True)

    print(f"Pulling all screenshots from {screenShotDir} to {outputDir}")

    # Pull entire screenshot folder contents to local_output_dir
    subprocess.run("adb pull " + screenShotDir + " " + outputDir, shell=True)

    # Delete all screenshots (.png files) on the device
    subprocess.run(f'adb shell su -c "rm {screenShotDir}*.png"', shell=True)
    print(f"Successfully pulled and deleted screenshots for test {test}, run {currentTestNo}")

    local_apc = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\outputGatord.apc"

    # Pull apc file
    pull_result = subprocess.run(
        r"adb pull /data/local/tmp/outputGatord.apc C:\Users\myd3192\Desktop\Unreal_Engine_ST2",
        shell=True
    )

    if pull_result.returncode != 0:
        print("ERROR: Failed to pull Gatord APC")
        return

    # Check that Gatord made a full APC folder before trying Streamline
    captured_xml = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\outputGatord.apc\captured.xml"

    if not os.path.exists(captured_xml):
        print(f"ERROR: Gatord APC is missing captured.xml: {captured_xml}")

        if os.path.exists(local_apc):
            print("Files inside APC folder:")
            print(os.listdir(local_apc))
        else:
            print("APC folder does not exist")

        return

    # Pull monotonic time
    subprocess.run("adb pull /data/local/tmp/monotonic_start.txt", shell=True)

    # Pull GameUserSettings.ini
    subprocess.run(
        "adb pull /sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Config/Android/GameUserSettings.ini GameUserSettings.ini",
        shell=True,
        check=True
    )

    # Pull Monotonic Frame Time from Game
    subprocess.run(
        "adb pull /sdcard/Android/data/com.YourCompany.SunTemple2/filesmonotonic_log.csv",
        shell=True
    )

    # Generate GPU CSV using APC file
    cli_path = r"C:\Program Files\Arm\Arm Performance Studio 2026.2\streamline\Streamline-cli.exe"
    apc_path = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\outputGatord.apc"

    subprocess.run(
        f'"{cli_path}" -report "{apc_path}" -format csv -output "{base_output_dir}"',
        shell=True,
        check=True
    )

    # Save raw APC folder before deleting it
    raw_apc_dir = os.path.join(base_output_dir, "Raw_Gatord_APC", folder)
    os.makedirs(raw_apc_dir, exist_ok=True)

    saved_apc_path = os.path.join(
        raw_apc_dir,
        f"outputGatord_test{test}_{run_no}.apc"
    )

    if os.path.exists(saved_apc_path):
        shutil.rmtree(saved_apc_path, ignore_errors=True)

    shutil.copytree(local_apc, saved_apc_path)

    # Rename CSV files based on test and run number
    # Copy files (Python-native, cross-platform)
    Output_Gatord_dir = os.path.join(base_output_dir, "Out_Gatord", folder)
    os.makedirs(Output_Gatord_dir, exist_ok=True)

    shutil.copy(
        os.path.join(base_output_dir, "timeline.csv"),
        os.path.join(Output_Gatord_dir, f"outputGatord_test{test}_{run_no}.csv")
    )

    perfetto_data_dir = os.path.join(base_output_dir, "Perfetto_Data", folder)
    os.makedirs(perfetto_data_dir, exist_ok=True)

    shutil.copy(
        "test_draft_perfetto.csv",
        os.path.join(perfetto_data_dir, f"perfettoData_test{test}_{run_no}.csv")
    )

    gator_ref_dir = os.path.join(base_output_dir, "GatorRef", folder)
    os.makedirs(gator_ref_dir, exist_ok=True)

    shutil.copy(
        "monotonic_start.txt",
        os.path.join(gator_ref_dir, f"gator_reference_time_test{test}_{run_no}.txt")
    )

    Mono_dir = os.path.join(base_output_dir, "MonotonicFrames", folder)
    os.makedirs(Mono_dir, exist_ok=True)

    shutil.copy(
        "filesmonotonic_log.csv",
        os.path.join(Mono_dir, f"monotonicFramesTime_test{test}_{run_no}.csv")
    )

    game_settings_dir = os.path.join(base_output_dir, "GameSettings", folder)
    os.makedirs(game_settings_dir, exist_ok=True)

    shutil.copy(
        "GameUserSettings.ini",
        os.path.join(game_settings_dir, f"GameUserSettings_test{test}_{run_no}.ini")
    )

    # Delete local files (cross-platform)
    # This only deletes the temporary local APC after it has been converted and saved
    if os.path.exists(local_apc):
        shutil.rmtree(local_apc, ignore_errors=True)

    for file in [
        "monotonic_start.txt",
        "GameUserSettings.ini",
        "filesmonotonic_log.csv",
        "test_draft_perfetto.csv"
    ]:
        if os.path.exists(file):
            os.remove(file)

    timeline_path = os.path.join(base_output_dir, "timeline.csv")
    if os.path.exists(timeline_path):
        os.remove(timeline_path)