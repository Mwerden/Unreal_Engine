#Code to generate teh different presets for graphical settings and to update and push teh graphical settings

import subprocess

# Choose different grpahical settings: Low, Medium, High, Epic, Cinematic

SCALABILITY_KEYS = [
    "sg.ResolutionQuality",
    "sg.ViewDistanceQuality",
    "sg.AntiAliasingQuality",
    "sg.ShadowQuality",
    "sg.GlobalIlluminationQuality",
    "sg.ReflectionQuality",
    "sg.PostProcessQuality",
    "sg.TextureQuality",
    "sg.EffectsQuality",
    "sg.FoliageQuality",
    "sg.ShadingQuality",
    "sg.LandscapeQuality"
]

LEVELS = ["Low", "Medium", "High", "Epic", "Cinematic"]
RESOLUTION_VALUES = [25, 50, 75, 90, 100]  # Mapping for sg.ResolutionQuality levels 0–4


def updateGameSettingini(values):

    # Pull current ini from device
    subprocess.run("adb pull /sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Config/Android/GameUserSettings.ini GameUserSettings.ini", shell=True, check=True)

    with open("GameUserSettings.ini", "r") as f:
        lines = f.readlines()

    new_lines = []
    in_scalability = False
    in_system = False

    # Track which keys we updated so we can add missing ones
    seen_keys = set()

    for line in lines:
        stripped = line.strip()
        matched = False

        # Detect sections
        if stripped == "[ScalabilityGroups]":
            in_scalability = True
        elif stripped.startswith("[") and stripped.endswith("]"):
            in_scalability = False

        # 🔧 NEW: detect system settings for resolution forcing
        if stripped == "[SystemSettings]":
            in_system = True
        elif stripped.startswith("[") and stripped.endswith("]"):
            in_system = False

        # Replace scalability values
        if in_scalability:
            for i, key in enumerate(SCALABILITY_KEYS):
                if stripped.startswith(key + "="):
                    matched = True
                    val = values[i]

                    if key == "sg.ResolutionQuality":
                        val = RESOLUTION_VALUES[val]

                    new_lines.append(f"{key}={val}\n")
                    seen_keys.add(key)
                    break

        if not matched:
            new_lines.append(line)

    # 🔧 NEW: Add missing scalability section if it doesn't exist
    if "[ScalabilityGroups]" not in "".join(lines):
        new_lines.append("\n[ScalabilityGroups]\n")
        for i, key in enumerate(SCALABILITY_KEYS):
            val = values[i]
            if key == "sg.ResolutionQuality":
                val = RESOLUTION_VALUES[val]
            new_lines.append(f"{key}={val}\n")

    # 🔧 NEW: FORCE resolution scaling (THIS IS WHY YOUR TESTS LOOKED THE SAME)
    # This guarantees Unreal actually uses the resolution change

    screen_percent = RESOLUTION_VALUES[values[0]]

    new_lines.append("\n[SystemSettings]\n")
    new_lines.append(f"r.ScreenPercentage={screen_percent}\n")
    new_lines.append(f"r.SecondaryScreenPercentage.GameViewport={screen_percent}\n")
    new_lines.append("r.DynamicRes.OperationMode=0\n")
    new_lines.append(f"r.DynamicRes.MinScreenPercentage={screen_percent}\n")
    new_lines.append(f"r.DynamicRes.MaxScreenPercentage={screen_percent}\n")

    # Write updated file
    with open("GameUserSettings.ini", "w") as f:
        f.writelines(new_lines)

    # Push back to device
    subprocess.run("adb push GameUserSettings.ini /sdcard/Android/data/com.YourCompany.SunTemple2/files/UnrealGame/SunTemple2/SunTemple2/Saved/Config/Android/GameUserSettings.ini", shell=True)


def generatePresets():
    all_presets = []
    num_settings = len(SCALABILITY_KEYS)
    NUM_LEVELS = len(LEVELS)

    # Baseline presets (0–4 for all settings)
    for level_idx in range(NUM_LEVELS):
        values = [level_idx] * num_settings
        all_presets.append(values)

    # Isolated variation (one setting at a time varied, rest set to Cinematic/4)
    cinematic_level = NUM_LEVELS - 1
    for setting_idx in range(num_settings):
        for level_idx in range(NUM_LEVELS - 1):  # 0 to 3
            values = [cinematic_level] * num_settings
            values[setting_idx] = level_idx
            all_presets.append(values)

    return all_presets


# 🔧 NEW: Helper for ONLY resolution tests (25 vs 100)
def generateResolutionOnlyPresets():
    return [
        [0, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # resolution = 25
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],  # resolution = 100
    ]