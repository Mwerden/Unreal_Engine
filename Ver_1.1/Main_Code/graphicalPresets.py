#This file will read the preset list, and figure out which setting is on and which setting is getting changed Such as ShadowQualityLow. THis will be used for organizing the data and naming the directories.
#Not tested yet.
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


def get_setting_folder(preset):
    # Check for baseline: all values the same
    if len(set(preset)) == 1:
        level_name = LEVELS[preset[0]] if SCALABILITY_KEYS[0] != "sg.ResolutionQuality" else f"{preset[0]}"
        return f"Baseline_{level_name}"

    # Check for single-setting variation: all cinematic except one
    cinematic_level = len(LEVELS) - 1
    varied_indices = [i for i, v in enumerate(preset) if v != cinematic_level]

    if len(varied_indices) == 1:
        idx = varied_indices[0]
        setting = SCALABILITY_KEYS[idx].split(".")[1]  # e.g., "sg.ShadowQuality" -> "ShadowQuality"
        level_value = preset[idx]
        if SCALABILITY_KEYS[idx] == "sg.ResolutionQuality":
            # ResolutionQuality is scaled 0–100, not 0–4
            res_map = {0: 25, 1: 50, 2: 75, 3: 90, 4: 100}  # Adjust if needed
            level_str = f"{res_map.get(level_value, level_value)}"
        else:
            level_str = LEVELS[level_value]

        return f"{setting}_{level_str}"

    return None
