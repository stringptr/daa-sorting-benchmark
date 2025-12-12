import json
import time
from pathlib import Path

# Output folder
LOG_DIR = Path("../results/instrument_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

DATA_DIR = Path("../data")   # <-- membaca instance JSON dari sini

# Batch otomatis
def get_batch(n, target_logs=100):
    return max(1, n // target_logs)


def log_progress(logs, ops, t_start, batch):
    if ops % batch == 0:
        logs.append({
            "ops": ops,
            "ms": (time.perf_counter() - t_start) * 1000
        })


# Insertion Sort (Instrumented)
def insertion_instrumented(arr):
    data = list(arr)
    n = len(data)
    batch = get_batch(n)

    logs = []
    ops = 0
    t_start = time.perf_counter()

    for i in range(1, n):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j+1] = data[j]
            j -= 1
            ops += 1
            log_progress(logs, ops, t_start, batch)
        data[j+1] = key

    total_ms = (time.perf_counter() - t_start) * 1000
    return data, logs, total_ms


# Merge Sort (Instrumented)
def merge_instrumented(arr):
    data = list(arr)
    n = len(data)
    batch = get_batch(n)

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
        while i < len(L) and j < len(R):
            ops += 1
            log_progress(logs, ops, t_start, batch)

            if L[i] <= R[j]:
                out.append(L[i])
                i += 1
            else:
                out.append(R[j])
                j += 1

        out.extend(L[i:])
        out.extend(R[j:])
        return out

    res = merge_sort(data)
    total_ms = (time.perf_counter() - t_start) * 1000
    return res, logs, total_ms


# Quick Sort (Instrumented)
def quick_instrumented(arr):
    data = list(arr)
    n = len(data)
    batch = get_batch(n)

    logs = []
    ops = 0
    t_start = time.perf_counter()

    def quicksort(a):
        nonlocal ops, logs
        if len(a) <= 1:
            return a

        pivot = a[len(a)//2]
        left, mid, right = [], [], []

        for x in a:
            ops += 1
            log_progress(logs, ops, t_start, batch)

            if x < pivot:
                left.append(x)
            elif x > pivot:
                right.append(x)
            else:
                mid.append(x)

        return quicksort(left) + mid + quicksort(right)

    res = quicksort(data)
    total_ms = (time.perf_counter() - t_start) * 1000
    return res, logs, total_ms

# Save JSON log
def save_log(algo, inst_id, n, logs, total_ms):
    fname = f"{algo}_inst{inst_id}_n{n}.json"
    out_path = LOG_DIR / fname

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "algo": algo,
            "instance_id": inst_id,
            "n": n,
            "total_ms": total_ms,
            "log_count": len(logs),
            "log": logs
        }, f, indent=2)

    print(f"[SAVED] {out_path}")


# AUTO-RUN SEMUA FILE JSON INSTANCES
if __name__ == "__main__":
    print("=== INSTRUMENTED BENCHMARK (AUTO MODE) ===")

    files = sorted(DATA_DIR.glob("sorting_near_sorted_*.json"))

    for f in files:
        inst_id = f.stem.split("_")[-1]

        with open(f, "r", encoding="utf-8") as fp:
            inst = json.load(fp)

        arr = inst["array"]
        n = inst["n"]

        print(f"\n>>> Instance {inst_id}, n={n}")

        # 3 algoritma
        for algo, func in [
            ("quick", quick_instrumented),
            ("merge", merge_instrumented),
            ("insertion", insertion_instrumented)
        ]:
            print(f"Running {algo}...")
            _, logs, total_ms = func(arr)
            save_log(algo, inst_id, n, logs, total_ms)

    print("\n=== DONE: Semua log instrumentasi dihasilkan ===")
