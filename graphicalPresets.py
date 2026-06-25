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
    "r.Upscale.Quality"
]

LEVELS = ["Low", "Medium", "High", "Epic", "Cinematic"]

UPSCALE_MAP = {
    0: "Bilinear",
    2: "CatmullRom",
    3: "Lanczos"
}


def get_setting_folder(preset):
    # Check for baseline: all values the same
    # Only check the normal scalability settings, not upscale
    normal_preset = preset[:12]

    if len(set(normal_preset)) == 1 and len(preset) == 12:
        level_name = LEVELS[normal_preset[0]]
        return f"Baseline_{level_name}"

    # NEW: Check for upscale test
    # Expected format: first 12 settings are cinematic, last value is upscale value
    if len(preset) == 13:
        normal_settings = preset[:12]
        upscale_value = preset[12]

        if all(v == 4 for v in normal_settings):
            upscale_name = UPSCALE_MAP.get(upscale_value, f"Value{upscale_value}")
            return f"UpscaleQuality_{upscale_name}"

    # Check for single-setting variation: all cinematic except one
    cinematic_level = len(LEVELS) - 1
    varied_indices = [i for i, v in enumerate(normal_preset) if v != cinematic_level]

    if len(varied_indices) == 1:
        idx = varied_indices[0]
        setting = SCALABILITY_KEYS[idx].split(".")[1]
        level_value = normal_preset[idx]

        if SCALABILITY_KEYS[idx] == "sg.ResolutionQuality":
            # ResolutionQuality is scaled 0–100, not 0–4
            res_map = {0: 25, 1: 50, 2: 75, 3: 90, 4: 100}
            level_str = f"{res_map.get(level_value, level_value)}"
        else:
            level_str = LEVELS[level_value]

        return f"{setting}_{level_str}"

    return None