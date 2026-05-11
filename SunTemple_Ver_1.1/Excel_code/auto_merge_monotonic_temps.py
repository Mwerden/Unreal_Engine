"""
auto_merge_monotonic_temps.py

Purpose:
    Loops through Test_01 to Test_56 in Temp_Test_Combo.xlsx, pulls the average
    temperature columns, then merges each test with that test's monotonic frame
    time file.

Expected folder setup:

    project_folder/
        Temp_Test_Combo.xlsx
        monotonic_files/
            Test_01_monotonic_log.csv
            Test_02_monotonic_log.csv
            ...
            Test_56_monotonic_log.csv
        merged_outputs/
            created automatically

Output per test:
    merged_outputs/Test_01_merged.csv
    merged_outputs/Test_02_merged.csv
    ...

Output columns:
    monotonic/frame timing columns + BIG_Avg, MID_Avg, LITTLE_Avg, G3D_Avg, SOC_Avg

Notes:
    - This uses the monotonic file as the master timeline.
    - Temps are matched to each frame using nearest previous temp time.
    - Your workbook temp time is in seconds.
"""

from pathlib import Path
import pandas as pd


# =========================
# USER SETTINGS
# =========================

TEMP_WORKBOOK = Path("Temp_Test_Combo.xlsx")
MONOTONIC_FOLDER = Path("monotonic_files")
OUTPUT_FOLDER = Path("merged_outputs")

# Change this if your monotonic files are named differently.
# Example expected name: Test_01_monotonic_log.csv
MONOTONIC_FILE_PATTERN = "{test_name}_monotonic_log.csv"

# Your temp workbook uses row 3 as the real header row.
TEMP_HEADER_ROW = 2  # pandas is zero-based, so Excel row 3 = 2

# Test sheets to process.
START_TEST = 1
END_TEST = 56

# If True, missing monotonic files are skipped instead of stopping the script.
SKIP_MISSING_MONOTONIC = True


# =========================
# HELPER FUNCTIONS
# =========================

def find_time_column(df):
    """Finds the most likely time column in a dataframe."""
    possible_names = [
        "time", "time_s", "time_sec", "time_seconds", "timestamp", "timestamp_s",
        "timestamp_ms", "time_ms", "monotonic", "monotonic_time", "monotonic_ns"
    ]

    cleaned = {str(col).strip().lower().replace(" ", "_").replace("(s)", "s").replace("(ms)", "ms"): col for col in df.columns}

    for name in possible_names:
        if name in cleaned:
            return cleaned[name]

    # Fallback: use the first numeric-looking column.
    for col in df.columns:
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.notna().sum() > 5:
            return col

    raise ValueError("Could not find a usable time column in the monotonic file.")


def convert_to_seconds(series, column_name):
    """Converts a time column to seconds based on the column name and value size."""
    values = pd.to_numeric(series, errors="coerce")
    name = str(column_name).lower()

    if "ns" in name:
        return values / 1_000_000_000
    if "us" in name:
        return values / 1_000_000
    if "ms" in name:
        return values / 1_000

    # Auto-detect if the values look too large to already be seconds.
    max_val = values.max(skipna=True)
    if pd.isna(max_val):
        return values

    # Nanoseconds usually look huge.
    if max_val > 1_000_000_000:
        return values / 1_000_000_000

    # Milliseconds often look like 0 to 240000 for a 240 second run.
    if max_val > 10_000:
        return values / 1_000

    # Otherwise assume seconds.
    return values


def load_temp_sheet(workbook_path, sheet_name):
    """Loads one Test_XX sheet and returns only time + average temp columns."""
    df = pd.read_excel(workbook_path, sheet_name=sheet_name, header=TEMP_HEADER_ROW)

    # These are the average columns from your workbook layout.
    needed_columns = ["Time (s)", "BIG Avg", "MID Avg", "LITTLE Avg", "G3D Avg", "SOC Avg"]

    missing = [col for col in needed_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{sheet_name} is missing columns: {missing}")

    temp = df[needed_columns].copy()
    temp = temp.rename(columns={
        "Time (s)": "time_s",
        "BIG Avg": "BIG_Avg",
        "MID Avg": "MID_Avg",
        "LITTLE Avg": "LITTLE_Avg",
        "G3D Avg": "G3D_Avg",
        "SOC Avg": "SOC_Avg",
    })

    # Convert formulas/blank cells to usable values.
    for col in temp.columns:
        temp[col] = pd.to_numeric(temp[col], errors="coerce")

    # Keep rows that have a valid time. Blank temp rows are okay, but they will stay blank.
    temp = temp.dropna(subset=["time_s"])

    # Remove rows where all temp averages are blank.
    temp_columns = ["BIG_Avg", "MID_Avg", "LITTLE_Avg", "G3D_Avg", "SOC_Avg"]
    temp = temp.dropna(subset=temp_columns, how="all")

    temp = temp.sort_values("time_s")
    return temp


def load_monotonic_file(monotonic_path):
    """Loads one monotonic CSV and creates a normalized time_s column."""
    mono = pd.read_csv(monotonic_path)

    time_col = find_time_column(mono)
    mono["time_s"] = convert_to_seconds(mono[time_col], time_col)
    mono = mono.dropna(subset=["time_s"])

    # Normalize start time to zero so it lines up with temp time.
    mono["time_s"] = mono["time_s"] - mono["time_s"].min()

    # Add frame timing if not already present.
    if "frame_time_s" not in mono.columns:
        mono["frame_time_s"] = mono["time_s"].diff()

    if "frame_time_ms" not in mono.columns:
        mono["frame_time_ms"] = mono["frame_time_s"] * 1000

    if "fps" not in mono.columns:
        mono["fps"] = 1 / mono["frame_time_s"]
        mono.loc[mono["frame_time_s"] <= 0, "fps"] = pd.NA

    mono = mono.sort_values("time_s")
    return mono


def merge_one_test(sheet_name):
    """Merges one temp sheet with its matching monotonic file."""
    monotonic_file = MONOTONIC_FOLDER / MONOTONIC_FILE_PATTERN.format(test_name=sheet_name)

    if not monotonic_file.exists():
        message = f"Missing monotonic file for {sheet_name}: {monotonic_file}"
        if SKIP_MISSING_MONOTONIC:
            print(f"SKIPPED: {message}")
            return None
        raise FileNotFoundError(message)

    temp = load_temp_sheet(TEMP_WORKBOOK, sheet_name)

    if temp.empty:
        print(f"SKIPPED: {sheet_name} has no filled temperature data")
        return None

    mono = load_monotonic_file(monotonic_file)

    # Match each frame to the nearest previous temperature sample.
    merged = pd.merge_asof(
        mono.sort_values("time_s"),
        temp.sort_values("time_s"),
        on="time_s",
        direction="backward"
    )

    # Optional: put the most important columns first.
    priority_cols = [
        "time_s", "frame_time_s", "frame_time_ms", "fps",
        "BIG_Avg", "MID_Avg", "LITTLE_Avg", "G3D_Avg", "SOC_Avg"
    ]
    other_cols = [col for col in merged.columns if col not in priority_cols]
    merged = merged[priority_cols + other_cols]

    output_path = OUTPUT_FOLDER / f"{sheet_name}_merged.csv"
    merged.to_csv(output_path, index=False)

    print(f"DONE: {sheet_name} -> {output_path}")
    return output_path


# =========================
# MAIN SCRIPT
# =========================

def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    if not TEMP_WORKBOOK.exists():
        raise FileNotFoundError(f"Could not find workbook: {TEMP_WORKBOOK}")

    if not MONOTONIC_FOLDER.exists():
        raise FileNotFoundError(f"Could not find monotonic folder: {MONOTONIC_FOLDER}")

    created_files = []

    for test_number in range(START_TEST, END_TEST + 1):
        sheet_name = f"Test_{test_number:02d}"
        result = merge_one_test(sheet_name)
        if result is not None:
            created_files.append(result)

    print("\n==============================")
    print(f"Created {len(created_files)} merged files")
    print("==============================")


if __name__ == "__main__":
    main()
