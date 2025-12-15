import json
import argparse
import time
from pathlib import Path
from typing import Any
from collections import Counter

# -------------------- ALGORITMA SORTING --------------------


def algo_A(instance: Any, project: str) -> Any:
    """QuickSort"""
    if project == "sorting":

        def quicksort(arr):
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x < pivot]
            middle = [x for x in arr if x == pivot]
            right = [x for x in arr if x > pivot]
            return quicksort(left) + middle + quicksort(right)

        return quicksort(list(instance["array"]))
    raise NotImplementedError(f"algo_A not implemented for project={project}")


def algo_B(instance: Any, project: str) -> Any:
    """MergeSort"""
    if project == "sorting":

        def merge_sort(a):
            if len(a) <= 1:
                return a
            m = len(a) // 2
            L = merge_sort(a[:m])
            R = merge_sort(a[m:])
            i = j = 0
            out = []
            while i < len(L) and j < len(R):
                if L[i] <= R[j]:
                    out.append(L[i])
                    i += 1
                else:
                    out.append(R[j])
                    j += 1
            out.extend(L[i:])
            out.extend(R[j:])
            return out

        return merge_sort(list(instance["array"]))
    raise NotImplementedError(f"algo_B not implemented for project={project}")


def algo_C(instance: Any, project: str) -> Any:
    """InsertionSort"""
    if project == "sorting":
        arr = list(instance["array"])
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    raise NotImplementedError(f"algo_C not implemented for project={project}")


# -------------------- EVALUATOR --------------------


def evaluate(instance: Any, output: Any, project: str) -> float:
    """Kembalikan metrik kualitas (0 = sempurna).
    Lengkapi evaluator sesuai proyek (gap, biaya, kelayakan, dsb.)."""
    if project == "sorting":
        # Reinforced validation: (1) urut non-decreasing, (2) elemen sama persis (multiset).
        # Untuk mencegah "lulus" jika ada elemen hilang/duplikat/berubah.
        if not isinstance(output, (list, tuple)):
            return 1.0

        original = instance.get("array", [])

        if len(output) != len(original):
            return 1.0

        is_sorted = all(output[i] <= output[i + 1] for i in range(len(output) - 1))
        if not is_sorted:
            return 1.0

        same_multiset = Counter(output) == Counter(original)
        return 0.0 if same_multiset else 1.0
    return 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--instance", required=True, help="Path ke berkas JSON di folder data/"
    )
    p.add_argument("--algo", choices=["A", "B", "C"], default="A")
    args = p.parse_args()

    inst = json.load(open(args.instance, "r", encoding="utf-8"))
    project = inst.get("project", "unknown")

    t0 = time.perf_counter()

    if args.algo == "A":
        out = algo_A(inst, project)
    elif args.algo == "B":
        out = algo_B(inst, project)
    elif args.algo == "C":
        out = algo_C(inst, project)
    else:
        print("Algoritma belum dipilih.")
        return

    dt = (time.perf_counter() - t0) * 1000.0
    gap = evaluate(inst, out, project)

    print(f"Project={project}  Algo={args.algo}  Time_ms={dt:.2f}  Gap={gap:.4f}")


if __name__ == "__main__":
    main()
