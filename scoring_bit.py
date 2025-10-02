import csv
import json
import os
import time
import tracemalloc
from pathlib import Path

# config
DECKS_DIR = "decks_chunks"
RESULTS_FILE = "results_2.csv"
PROGRESS_FILE = "progress_2.json"

DECK_SIZE_BITS = 52
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8

# sequences and matchups
SEQUENCES = [
    "000", "001", "010", "011",
    "100", "101", "110", "111",
]
MATCHUPS = [(p1, p2) for i, p1 in enumerate(SEQUENCES) for j, p2 in enumerate(SEQUENCES) if i != j]

# progress tracking
def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"matchup_index": 0, "file_index": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# results
def load_results():
    results = {}
    if Path(RESULTS_FILE).exists():
        with open(RESULTS_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["p1_seq"], row["p2_seq"])
                results[key] = {
                    "p1_tricks": int(row["p1_tricks"]),
                    "p2_tricks": int(row["p2_tricks"]),
                    "draws_tricks": int(row["draws_tricks"]),
                    "p1_cards": int(row["p1_cards"]),
                    "p2_cards": int(row["p2_cards"]),
                    "draws_cards": int(row["draws_cards"]),
                    "runs": int(row["runs"]),
                }
    return results

def save_results(results):
    fieldnames = [
        "p1_seq", "p2_seq",
        "p1_tricks", "p2_tricks", "draws_tricks",
        "p1_cards", "p2_cards", "draws_cards",
        "runs",
    ]
    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (p1_seq, p2_seq), vals in results.items():
            writer.writerow({
                "p1_seq": p1_seq,
                "p2_seq": p2_seq,
                **vals
            })

# read decks
def read_decks_from_file(filename):
    decks = []
    with open(filename, "rb") as f:
        while (chunk := f.read(BYTES_PER_DECK)):
            deck_int = int.from_bytes(chunk, "big")
            decks.append(deck_int)
    return decks

# play one deck
def play_deck(deck_int, p1_seq, p2_seq):
    i = 0
    n = DECK_SIZE_BITS
    p1_tricks = p2_tricks = 0
    p1_cards = p2_cards = 0

    p1_bits = int(p1_seq, 2)
    p2_bits = int(p2_seq, 2)

    while i <= n - 3:
        window = (deck_int >> (n - 3 - i)) & 0b111
        if window == p1_bits:
            p1_tricks += 1
            p1_cards += (i + 3)
            n -= (i + 3)
            deck_int &= (1 << n) - 1
            i = 0
            continue
        elif window == p2_bits:
            p2_tricks += 1
            p2_cards += (i + 3)
            n -= (i + 3)
            deck_int &= (1 << n) - 1
            i = 0
            continue
        i += 1

    draws_tricks = 1 if p1_tricks == p2_tricks else 0
    draws_cards = 1 if p1_cards == p2_cards else 0

    return p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards

# main loop
def main():
    progress = load_progress()
    matchup_index = progress["matchup_index"]
    file_index = progress["file_index"]

    deck_file = os.path.join(DECKS_DIR, f"decks_seed{file_index+1:03d}.bin")
    if not Path(deck_file).exists():
        print(f"No more deck files to process at index {file_index}. Done!")
        return

    # start runtime + memory
    start_time = time.perf_counter()
    tracemalloc.start()

    decks = read_decks_from_file(deck_file)
    print(f"Processing file: {deck_file} with {len(decks)} decks...")

    results = load_results()

    for deck_int in decks:
        p1_seq, p2_seq = MATCHUPS[matchup_index]
        p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards = play_deck(deck_int, p1_seq, p2_seq)

        key = (p1_seq, p2_seq)
        if key not in results:
            results[key] = {
                "p1_tricks": 0,
                "p2_tricks": 0,
                "draws_tricks": 0,
                "p1_cards": 0,
                "p2_cards": 0,
                "draws_cards": 0,
                "runs": 0,
            }

        results[key]["p1_tricks"] += p1_tricks
        results[key]["p2_tricks"] += p2_tricks
        results[key]["draws_tricks"] += draws_tricks
        results[key]["p1_cards"] += p1_cards
        results[key]["p2_cards"] += p2_cards
        results[key]["draws_cards"] += draws_cards
        results[key]["runs"] += 1

        matchup_index = (matchup_index + 1) % len(MATCHUPS)

    save_results(results)

    progress["matchup_index"] = matchup_index
    progress["file_index"] = file_index + 1
    save_progress(progress)

    # end runtime + memory
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Finished file {file_index+1}. Next run will use file index {file_index+1}.")
    print(f"Runtime: {elapsed:.2f} seconds | Peak memory: {peak / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
