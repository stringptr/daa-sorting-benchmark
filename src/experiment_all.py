import subprocess
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_CSV = RESULTS_DIR / "run_results.csv"

ALGOS = ["A", "B", "C"]  # QuickSort, MergeSort, InsertionSort


def run_experiment(instance_path, algo):
    """Jalankan run.py dan ambil output string-nya."""
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

    # Expected format:
    # Project=sorting  Algo=A  Time_ms=12.34  Gap=0.0000
    parts = out.split()
    time_ms = float(parts[2].split("=")[1])
    gap = float(parts[3].split("=")[1])

    return time_ms, gap


def extract_metadata(instance_path):
    """Ambil metadata n & error dari file instance JSON."""
    with open(instance_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["n"], data["error"]


def main():
    instances = sorted(DATA_DIR.glob("*.json"))

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "n", "error", "algo", "time_ms", "gap"])

        for inst in instances:
            n, error = extract_metadata(inst)

            for algo in ALGOS:
                time_ms, gap = run_experiment(inst, algo)
                writer.writerow([inst.name, n, error, algo, time_ms, gap])

    print("\n=== DONE: Semua eksperimen selesai dan tersimpan di results/run_results.csv ===")


if __name__ == "__main__":
    main()
