from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = r"C:\Users\Micah\Desktop\Monotonic_Temo_Merge\Best_Data_Output_FIXED.xlsx"
OUTPUT_FOLDER = r"C:\Users\Micah\Desktop\Monotonic_Temo_Merge\FPS_Graphs"
OUTPUT_BOXPLOT = "FPS_Boxplot_BASELINE_EPIC_HIGH_MEDIUM_LOW.png"

MIN_FPS = 0
MAX_FPS = 90

Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

skip_sheets = [
    "Summary",
    "Clean_Summary",
    "Mapping",
    "Temp_All",
    "Merged_All",
    "Original_Summary"
]

level_order = {
    "Epic": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3
}

group_order = [
    "Baseline",
    "AntiAliasingQuality",
    "ViewDistanceQuality",
    "ShadowQuality",
    "GlobalIlluminationQuality",
    "ReflectionQuality",
    "PostProcessQuality",
    "TextureQuality",
    "EffectsQuality",
    "FoliageQuality",
    "ResolutionQuality"
]


def get_group_and_level(sheet_name):
    if sheet_name.startswith("Baseline_"):
        return "Baseline", sheet_name.split("_")[1]

    if "_" in sheet_name:
        group, level = sheet_name.rsplit("_", 1)
        return group, level

    return sheet_name, ""


def sort_key(sheet_name):
    group, level = get_group_and_level(sheet_name)

    if group == "Baseline":
        try:
            return (0, int(level))
        except:
            return (0, 99)

    try:
        group_index = group_order.index(group)
    except ValueError:
        group_index = 99

    # Resolution uses numeric values, but keep high-to-low style:
    # 100, 90, 75, 50, 25 if present
    if group == "ResolutionQuality":
        resolution_order = {
            "100": 0,
            "90": 1,
            "75": 2,
            "50": 3,
            "25": 4
        }
        return (group_index, resolution_order.get(level, 99))

    return (group_index, level_order.get(level, 99))


excel = pd.ExcelFile(INPUT_FILE)

sheet_names = []
for sheet in excel.sheet_names:
    if sheet in skip_sheets:
        continue

    df_check = pd.read_excel(INPUT_FILE, sheet_name=sheet, nrows=5)

    if "fps" in df_check.columns:
        sheet_names.append(sheet)

sheet_names = sorted(sheet_names, key=sort_key)

print("Graph order:")
for s in sheet_names:
    print(s)

fps_data = []
labels = []
summary_rows = []

for sheet in sheet_names:
    df = pd.read_excel(INPUT_FILE, sheet_name=sheet)

    df["fps"] = pd.to_numeric(df["fps"], errors="coerce")
    df = df.dropna(subset=["fps"])

    df = df[(df["fps"] >= MIN_FPS) & (df["fps"] <= MAX_FPS)]

    if df.empty:
        print(f"Skipping {sheet}: no FPS data after filtering")
        continue

    fps_data.append(df["fps"])
    labels.append(sheet)

    summary_rows.append({
        "setting": sheet,
        "avg_fps": round(df["fps"].mean(), 2),
        "median_fps": round(df["fps"].median(), 2),
        "min_fps": round(df["fps"].min(), 2),
        "max_fps": round(df["fps"].max(), 2),
        "std_fps": round(df["fps"].std(), 2),
        "sample_count": len(df)
    })

if len(fps_data) == 0:
    raise RuntimeError("No FPS data found. Check that Best_Data_Output_FIXED.xlsx has fps columns.")

plt.figure(figsize=(22, 8))

plt.boxplot(
    fps_data,
    labels=labels,
    showmeans=True,
    showfliers=False,
    widths=0.45
)

plt.axhline(60, linestyle="-", linewidth=1, label="60 FPS")
plt.axhline(30, linestyle="--", linewidth=1, label="30 FPS")

plt.title("FPS Distribution per Graphics Setting")
plt.xlabel("Graphics Setting")
plt.ylabel("FPS")
plt.ylim(MIN_FPS, MAX_FPS)
plt.xticks(rotation=65, ha="right", fontsize=8)
plt.grid(True, axis="y", alpha=0.3)
plt.legend()
plt.tight_layout()

box_output = Path(OUTPUT_FOLDER) / OUTPUT_BOXPLOT
plt.savefig(box_output, dpi=300)
plt.close()

summary_df = pd.DataFrame(summary_rows)
summary_path = Path(OUTPUT_FOLDER) / "FPS_Boxplot_Ordered_Summary.xlsx"
summary_df.to_excel(summary_path, index=False)

print("DONE")
print(f"Graph saved to: {box_output}")
print(f"Summary saved to: {summary_path}")