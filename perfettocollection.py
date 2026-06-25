import subprocess
import pandas as pd
import re
from perfetto.trace_processor import TraceProcessor, TraceProcessorConfig
import os

# Function to write and push the perfetto configuration file to the phone

TRACE_PROCESSOR_PATH = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\windows-amd64"
def writeConfig(duration):
    # Writing config file
    with open("perfettoConfig.pbtxt", "w") as f:
        f.write('buffers: {\n')
        f.write('  size_kb: 1024\n')
        f.write('}\n\n')
        f.write('duration_ms:' + str(duration * 1000) + '\n\n')  # Writes the duration of the config file
        f.write('data_sources: {\n')
        f.write('    config {\n')
        f.write('        name: "android.power"\n')
        f.write('        android_power_config {\n')
        f.write('            battery_poll_ms: 200\n')
        f.write('            collect_power_rails: true\n')
        f.write('    }\n')
        f.write('  }\n')
        f.write('}\n')
        f.close()
    print("Finished creating Config file now pushing File to Phone")
    subprocess.run("adb push perfettoConfig.pbtxt /data/local/tmp", shell=True)
    # Push and write the config file


def extract_trace_start_ns():
    result = subprocess.run(
        f'"{TRACE_PROCESSOR_PATH}" energy_test_out --query-string "SELECT str_value, int_value FROM metadata WHERE name = \'tracing_started_ns\';"',
        shell=True,
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():
        match = re.search(r'(\d+)', line)
        if match:
            return int(match.group(1)) / 1e6  # Convert ns to ms

    return None


# TODO Need to make sure Perfetto runs only one one core.
# Function ran as thread to run the perfetto tool
def perfettoPowerData(time_duration, startEvent):
    writeConfig(time_duration)
    # barrier.wait()
    startEvent.wait()

    subprocess.run(
        [
            "adb", "shell", "su", "-c",
            f"taskset 020 /data/local/tmp/perfetto -c /data/local/tmp/perfettoConfig.pbtxt -o /data/local/tmp/energy_test_out --txt"
        ],
        check=True
    )  # Runs perfetto on Core 020

    # time.sleep(time_duration +5)
    # subprocess.run('chmod 644 energy_test_out', shell=True)  # permission for rooted user to do what they want to do with file

    print("Pulling Data")
    subprocess.run(["adb", "pull", "/data/local/tmp/energy_test_out"], check=True)  # pulls data to computer

    print("Making CSV")

    trace_path = "energy_test_out"

    TRACE_PROCESSOR_PATH = r"C:\Users\myd3192\Desktop\Unreal_Engine_ST2\windows-amd64\trace_processor_shell.exe"




    if not os.path.exists(trace_path):
        print(" Trace file missing")
        return

    if not os.path.exists(TRACE_PROCESSOR_PATH):
        print(" Trace processor not found:", TRACE_PROCESSOR_PATH)
        return

    config = TraceProcessorConfig(
        bin_path=TRACE_PROCESSOR_PATH
    )

    tp = TraceProcessor(trace=trace_path, config=config)
    query = """
        SELECT
            ct.name AS rail_name,
            c.ts / 1e6 AS timestamp_ms,
            c.value
        FROM counter c
        JOIN counter_track ct ON c.track_id = ct.id
        WHERE ct.name LIKE '%power%' OR ct.name LIKE '%rail%'
        ORDER BY timestamp_ms;
        """

    result = tp.query(query)

    with open("power_railsTEST.csv", "w", newline="") as f:
        f.write("rail_name,timestamp_ms,value\n")
        for row in result:
            f.write(f"{row.rail_name},{row.timestamp_ms},{row.value}\n")

    convertPerfettoCSV()


def convertPerfettoCSV():
    if not os.path.exists("power_railsTEST.csv") or os.path.getsize("power_railsTEST.csv") == 0:
        print(" CSV missing or empty")
        return

    df = pd.read_csv("power_railsTEST.csv")
    df = df.drop_duplicates()  # Gets rid of the duplicate rows

    flipRowsAndColumns = df.pivot(index="timestamp_ms", columns="rail_name", values="value")
    flipRowsAndColumns = flipRowsAndColumns.reset_index()  # Timestamp is now a column not index
    flipRowsAndColumns = flipRowsAndColumns.sort_values("timestamp_ms")  # sorts by timestamp

    flipRowsAndColumns['timestamp_ms'] = flipRowsAndColumns['timestamp_ms'] / 1000
    flipRowsAndColumns = flipRowsAndColumns.rename(columns={"timestamp_ms": "timestamp_sec"})

    # code to make it seconds
    # flipRowsAndColumns = flipRowsAndColumns.rename(columns={"timestamp_sec":  "seconds"})
    # flipRowsAndColumns["seconds"] = flipRowsAndColumns["seconds"]- trace_start_time

    # print(flipRowsAndColumns.columns.tolist())
    print("Making CSV")
    flipRowsAndColumns.to_csv("test_draft_perfetto.csv", index=False)


if __name__ == "__main__":
    pass
    # convertPerfettoCSV(89911803.632117/1000)
