# DAA Sorting Benchmark (Near-Sorted Instances)

This repo benchmarks **three sorting algorithms** on **near-sorted** arrays (arrays that are almost sorted, with a controlled amount of disorder).

**Algorithms**
- **Algo A**: QuickSort (pivot = middle element)
- **Algo B**: MergeSort
- **Algo C**: Insertion Sort

> Note: The `data/` folder is ignored by Git (see `.gitignore`). Generate instances locally using the command below.

---

## Project Structure

- `src/run.py` — run a single algorithm on one instance (prints runtime + gap).
- `src/generate_instances.py` — generate instance JSON files into `data/`.
- `src/experiment_all.py` — run all instances × all algorithms → `results/run_results.csv`.
- `src/experiment_variance.py` — repeated runs for selected instances → `results/variance_runs.csv`.
- `src/instrumented_benchmark.py` — generate instrument logs (ops vs time) → `results/instrument_logs/*.json`.
- `analysis/SortingBenchmark.ipynb` — analysis + plots.

---

## Setup

Python 3.10+ recommended.

Install dependencies (minimal):
```bash
pip install -r requirements.txt
```

---

## Generate Instances

```bash
python src/generate_instances.py
```

This creates 15 JSON instances:
- `n ∈ {1000, 5000, 20000, 100000, 500000}`
- `error ∈ {0.02, 0.05, 0.10}`

---

## Run One Instance

```bash
python src/run.py --instance data/sorting_near_sorted_1.json --algo A
python src/run.py --instance data/sorting_near_sorted_1.json --algo B
python src/run.py --instance data/sorting_near_sorted_1.json --algo C
```

Output format:
```
Project=sorting Algo=A Time_ms=... Gap=...
```

---

## Run Full Benchmark

```bash
python src/experiment_all.py
```

Outputs:
- `results/run_results.csv`

---

## Variance Experiment (Repeated Runs)

```bash
python src/experiment_variance.py
```

Outputs:
- `results/variance_runs.csv`

---

## Instrumented Logs (Ops vs Time)

```bash
python src/instrumented_benchmark.py
```

Optional parameters:
```bash
python src/instrumented_benchmark.py --target-logs 200
python src/instrumented_benchmark.py --algos quick,merge
python src/instrumented_benchmark.py --pattern "sorting_near_sorted_*.json"
```

Outputs:
- `results/instrument_logs/*.json`

---

## Analysis / Plots

Open:
- `analysis/SortingBenchmark.ipynb`

The notebook reads:
- `results/run_results.csv`
- `results/variance_runs.csv`
- `results/instrument_logs/*.json`
