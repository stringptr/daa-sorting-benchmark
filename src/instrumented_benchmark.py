import argparse
import json
import time
from pathlib import Path

# Resolve repo root regardless of where the script is executed from
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_LOG_DIR = ROOT / "results" / "instrument_logs"


def get_batch(n: int, target_logs: int = 100) -> int:
    """Return a sampling batch so we log roughly `target_logs` points."""
    return max(1, n // max(1, target_logs))


def log_progress(logs, ops, t_start, batch):
    if batch > 0 and ops % batch == 0:
        logs.append({"ops": ops, "ms": (time.perf_counter() - t_start) * 1000})


# -------------------- Instrumented Sorting Algorithms --------------------

def insertion_instrumented(arr, target_logs: int = 100):
    data = list(arr)
    n = len(data)
    batch = get_batch(n, target_logs)

    logs = []
    ops = 0
    t_start = time.perf_counter()

    for i in range(1, n):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            ops += 1
            log_progress(logs, ops, t_start, batch)
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key

    total_ms = (time.perf_counter() - t_start) * 1000
    return data, logs, total_ms


def merge_instrumented(arr, target_logs: int = 100):
    data = list(arr)
    n = len(data)
    batch = get_batch(n, target_logs)

    logs = []
    ops = 0
    t_start = time.perf_counter()

    def merge_sort(a):
        nonlocal ops, logs
        if len(a) <= 1:
            return a

        m = len(a) // 2
        L = merge_sort(a[:m])
        R = merge_sort(a[m:])

        i = j = 0
        out = []

        # merge
        while i < len(L) and j < len(R):
            ops += 1
            log_progress(logs, ops, t_start, batch)
            if L[i] <= R[j]:
                out.append(L[i]); i += 1
            else:
                out.append(R[j]); j += 1

        out.extend(L[i:])
        out.extend(R[j:])
        return out

    res = merge_sort(data)
    total_ms = (time.perf_counter() - t_start) * 1000
    return res, logs, total_ms


def quick_instrumented(arr, target_logs: int = 100):
    """QuickSort instrumented to mirror src/run.py (3 passes per partition)."""
    data = list(arr)
    n = len(data)
    batch = get_batch(n, target_logs)

    logs = []
    ops = 0
    t_start = time.perf_counter()

    def quicksort(a):
        nonlocal ops, logs
        if len(a) <= 1:
            return a

        pivot = a[len(a) // 2]

        left = []
        for x in a:
            ops += 1
            log_progress(logs, ops, t_start, batch)
            if x < pivot:
                left.append(x)

        mid = []
        for x in a:
            ops += 1
            log_progress(logs, ops, t_start, batch)
            if x == pivot:
                mid.append(x)

        right = []
        for x in a:
            ops += 1
            log_progress(logs, ops, t_start, batch)
            if x > pivot:
                right.append(x)

        return quicksort(left) + mid + quicksort(right)

    res = quicksort(data)
    total_ms = (time.perf_counter() - t_start) * 1000
    return res, logs, total_ms


def save_log(out_dir: Path, algo: str, inst_id: int, n: int, error: float | None, logs, total_ms: float):
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{algo}_inst{inst_id}_n{n}.json"
    out_path = out_dir / fname

    payload = {
        "algo": algo,
        "instance_id": int(inst_id),
        "n": int(n),
        "error": None if error is None else float(error),
        "total_ms": float(total_ms),
        "log_count": int(len(logs)),
        "log": logs,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[SAVED] {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate instrumented logs (ops vs time) for sorting instances.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing instance JSON files.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_LOG_DIR, help="Directory to write instrument logs.")
    parser.add_argument("--pattern", type=str, default="sorting_near_sorted_*.json", help="Glob pattern for instances.")
    parser.add_argument("--target-logs", type=int, default=100, help="Approx number of log points per run.")
    parser.add_argument("--algos", type=str, default="quick,merge,insertion",
                        help="Comma-separated list: quick, merge, insertion")
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    out_dir: Path = args.out_dir
    pattern: str = args.pattern
    target_logs: int = args.target_logs
    algos = [a.strip().lower() for a in args.algos.split(",") if a.strip()]

    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}. Run: python src/generate_instances.py")

    files = sorted(data_dir.glob(pattern))
    if not files:
        raise SystemExit(f"No instance files matched pattern '{pattern}' in {data_dir}")

    algo_map = {
        "quick": quick_instrumented,
        "merge": merge_instrumented,
        "insertion": insertion_instrumented,
    }

    selected = []
    for a in algos:
        if a not in algo_map:
            raise SystemExit(f"Unknown algo '{a}'. Choose from: {', '.join(algo_map)}")
        selected.append((a, algo_map[a]))

    print("=== INSTRUMENTED BENCHMARK ===")
    print(f"Data: {data_dir}")
    print(f"Out : {out_dir}")
    print(f"Files matched: {len(files)}")
    print(f"Algos: {', '.join([a for a,_ in selected])}")
    print(f"Target logs per run: ~{target_logs}")

    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            inst = json.load(fp)

        inst_id = int(inst.get("instance_id", f.stem.split("_")[-1]))
        arr = inst["array"]
        n = inst["n"]
        error = inst.get("error", None)

        print(f"\n>>> Instance {inst_id}, n={n}, error={error}")

        for algo, func in selected:
            print(f"Running {algo}...")
            _, logs, total_ms = func(arr, target_logs=target_logs)
            save_log(out_dir, algo, inst_id, n, error, logs, total_ms)

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
