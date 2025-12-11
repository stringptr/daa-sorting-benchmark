# DAA_Instances/generate_instances.py
import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent / "data"
BASE.mkdir(exist_ok=True)


def save(name, obj):
    p = BASE / name
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return p


def make_sorting_near_sorted(n=2000, perturb_percent=0.10, max_dist=10, seed=42):
    """
    Stronger Near-Sorted variant (Near-A):
    - Start sorted
    - Select perturb_percent of elements to move slightly (±max_dist)
    - Perform local displacements, not simple swaps
    """
    arr = list(range(n))
    rnd = random.Random(seed)

    k = int(n * perturb_percent)
    indices = rnd.sample(range(n), k)
    indices.sort()

    for i in indices:
        new_pos = i + rnd.randint(-max_dist, max_dist)
        new_pos = max(0, min(n - 1, new_pos))
        val = arr.pop(i)
        arr.insert(new_pos, val)

    return arr


def main():
    sizes = [1000, 5000, 20000, 100000, 500000]
    errors = [0.02, 0.05, 0.10]
    max_dist = 8

    seed_base = 123  # supaya reproducible

    count = 1
    for n in sizes:
        for e in errors:
            arr = make_sorting_near_sorted(
                n=n, perturb_percent=e, max_dist=max_dist, seed=seed_base + count
            )
            fname = f"sorting_near_sorted_{count}.json"
            save(
                fname,
                {
                    "project": "sorting",
                    "description": "Near Sorted Array",
                    "n": n,
                    "error": e,
                    "array": arr,
                },
            )
            count += 1

    print("OK: All near-sorted datasets generated!")


if __name__ == "__main__":
    main()
