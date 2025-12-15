import subprocess
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_CSV = RESULTS_DIR / "variance_runs.csv"

# pilih instance tertentu untuk diuji variansi
TARGET_INSTANCES = [
    "sorting_near_sorted_3.json",
    "sorting_near_sorted_9.json",
    "sorting_near_sorted_12.json",
]

ALGOS = ["A", "B", "C"]   # QuickSort, MergeSort, InsertionSort
REPEATS = 50              # jumlah pengulangan per algo per instance


def run_experiment(instance_path, algo):
    """Jalankan run.py dan ambil output waktu runtime."""
    run_py = ROOT / "src" / "run.py"

    cmd = [
        "python",
        str(run_py),
        "--instance",
        str(instance_path),
        "--algo",
        algo,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout.strip()
    print(out)

    # Expected:
    # Project=sorting  Algo=A  Time_ms=0.50  Gap=0.0000
    parts = out.split()
    time_ms = float(parts[2].split("=")[1])
    return time_ms


def extract_metadata(instance_path):
    with open(instance_path, "r") as f:
        js = json.load(f)
    return js["n"], js["error"]


def main():
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "n", "error", "algo", "run_id", "time_ms"])

        for filename in TARGET_INSTANCES:
            inst_path = DATA_DIR / filename
            n, error = extract_metadata(inst_path)

            print(f"\n=== Variance test for {filename} ===")

            for algo in ALGOS:
                print(f"\n> Algo {algo}")

                for r in range(1, REPEATS + 1):
                    time_ms = run_experiment(inst_path, algo)
                    writer.writerow([filename, n, error, algo, r, time_ms])

    print("\n=== DONE: Variance experiment selesai. Saved to results/variance_runs.csv ===")


if __name__ == "__main__":
    main()
