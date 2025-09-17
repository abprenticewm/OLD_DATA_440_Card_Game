# run_tests.py: 
# generates decks in chunks, stores them, reloads them,
# and records per-file runtime and sizes in a CSV file & table

# imports
import argparse
import time
import os
import csv
from array import array
from pathlib import Path
import random
import statistics   # NEW: for mean/stddev

from src.decks import generate_deck, decode_deck

# math for chunking
DECKS_PER_FILE = 10_000   # chunk size for text files

# helper to convert bytes to mb
def bytes_to_mb(b: int) -> float:
    return b / (1024**2)

# helper to format time nicely
def formatted_time(s: float) -> str:
    return f"{s:.3f} s" if s >= 1 else f"{s*1000:.1f} ms"

# run one full test
def run_once(N, outdir, quick=False):
    # creates a path object for the folder where user want to save the output files  
    Path(outdir).mkdir(parents=True, exist_ok=True)

    # prepare table headers and rows for results
    headers = ["File", "Decks", "Gen Time", "Write Time", "Read Time", "Size (MB)"]
    rows = []

    # start total timer
    time_total = time.perf_counter()
    # totals across all files
    total_gen = 0.0
    total_write = 0.0
    total_read = 0.0

    # loop over files
    num_files = (N + DECKS_PER_FILE - 1) // DECKS_PER_FILE
    for file_idx in range(num_files):
        start = file_idx * DECKS_PER_FILE
        end = min((file_idx + 1) * DECKS_PER_FILE, N)
        count = end - start

        rng = random.Random(file_idx)

        # generation
        t0 = time.perf_counter()
        decks = [decode_deck(generate_deck(rng)) for _ in range(count)]
        t1 = time.perf_counter()

        # write
        filename = Path(outdir) / f"decks_{file_idx:04d}.txt"
        t2 = time.perf_counter()
        with open(filename, "w") as f:
            f.write("\n".join(decks) + "\n")
        t3 = time.perf_counter()
        size = os.path.getsize(filename)

        # read
        t4 = time.perf_counter()
        with open(filename, "r") as f:
            loaded = f.read().splitlines()
        t5 = time.perf_counter()

        # update totals
        total_gen += (t1 - t0)
        total_write += (t3 - t2)
        total_read += (t5 - t4)

        # record per-file row
        rows.append([
            filename.name,
            f"{count:,}",
            formatted_time(t1 - t0),
            formatted_time(t3 - t2),
            formatted_time(t5 - t4),
            f"{bytes_to_mb(size):.2f}"
        ])

    # end total timer
    total_runtime = time.perf_counter() - time_total

    return rows, total_gen, total_write, total_read, total_runtime


# main function to run the tests
def main():
    # command-line args
    parser = argparse.ArgumentParser()
    # allows user to change the number of decks with a default of 2 million
    parser.add_argument("--n", type=int, default=2_000_000, help="Number of decks")
    # allows user to create a folder for output files
    parser.add_argument("--outdir", default="out", help="Output directory")
    # allows user the option to do a quick test with 50k decks
    parser.add_argument("--quick", action="store_true", help="Quick test (50k decks)")
    # allows user to run multiple tests for stats
    parser.add_argument("--runs", type=int, default=1, help="Repeat test this many times")  # NEW
    args = parser.parse_args()

    # determine number of decks depenting on if user wants a quick test or not
    N = 50_000 if args.quick else args.n
    print(f"\nRunning with N = {N:,} decks")
    print(f"{DECKS_PER_FILE:,} decks per file (≈{DECKS_PER_FILE*53/1024:.1f} KB/file)")

    # collect results across runs
    gen_times, write_times, read_times, runtimes = [], [], [], []
    # run the tests
    for run_idx in range(args.runs):
        print(f"\n--- Run {run_idx+1}/{args.runs} ---")
        rows, total_gen, total_write, total_read, total_runtime = run_once(N, args.outdir, args.quick)

        # print per-file table
        headers = ["File", "Decks", "Gen Time", "Write Time", "Read Time", "Size (MB)"]
        col_widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
        print(" | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)))
        print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
        for row in rows:
            print(" | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers))))

        # print summary totals for this run
        print("\n=== Summary (this run) ===")
        num_files = (N + DECKS_PER_FILE - 1) // DECKS_PER_FILE
        print(f"Total decks: {N:,}")
        print(f"Files written: {num_files}")
        print(f"Total generation time: {formatted_time(total_gen)}")
        print(f"Total write time:      {formatted_time(total_write)}")
        print(f"Total read time:       {formatted_time(total_read)}")
        print(f"Total runtime:         {formatted_time(total_runtime)}")

        # save CSV for this run (overwrite each run)
        with open("results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"\nPer-file results saved to 'results.csv'")

        # sample decks
        print("\nSample decks from first file:")
        with open(Path(args.outdir) / "decks_0000.txt", "r") as f:
            for i, line in enumerate(f):
                if i >= 3:
                    break
                print(f" Deck {i+1}: {line.strip()}")

        # collect stats
        gen_times.append(total_gen)
        write_times.append(total_write)
        read_times.append(total_read)
        runtimes.append(total_runtime)

    # after all runs, show stats if multiple runs
    if args.runs > 1:
        print("\n=== Averages over runs ===")
        def show_stats(label, vals):
            print(f"{label:<20} mean={statistics.mean(vals):.3f}s  std={statistics.stdev(vals):.3f}s")
        show_stats("Generation", gen_times)
        show_stats("Write", write_times)
        show_stats("Read", read_times)
        show_stats("Total runtime", runtimes)


# run main if this file is executed
if __name__ == "__main__":
    main()
