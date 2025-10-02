import csv
import json
import os
import time
import tracemalloc
from pathlib import Path

# folder with deck files
DECKS_DIR = "decks_chunks"
# where results are saved
RESULTS_FILE = "results.csv"
# where progress is tracked
PROGRESS_FILE = "progress.json"

# number of bits per deck
DECK_SIZE_BITS = 52
# number of bytes needed to hold one deck
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8

# possible 3-bit sequences
SEQUENCES = [
    "000", "001", "010", "011",
    "100", "101", "110", "111",
]

# all possible matchups (exclude identical)
MATCHUPS = [(p1, p2) for i, p1 in enumerate(SEQUENCES) for j, p2 in enumerate(SEQUENCES) if i != j]


def load_progress():
    # load progress if file exists, else start fresh
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"matchup_index": 0, "file_index": 0}


def save_progress(progress):
    # save progress to file
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def load_results():
    # load results into dictionary
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
    # write results back to CSV
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


def read_decks_from_file(filename):
    # read decks as binary, convert to 52-bit strings
    decks = []
    with open(filename, "rb") as f:
        while (chunk := f.read(BYTES_PER_DECK)):
            deck_int = int.from_bytes(chunk, "big")
            deck_bits = format(deck_int, f"0{DECK_SIZE_BITS}b")
            decks.append(deck_bits)
    return decks


def play_deck(deck_bits, p1_seq, p2_seq):
    # simulate one game with given deck
    i = 0
    n = len(deck_bits)
    p1_tricks = p2_tricks = 0
    p1_cards = p2_cards = 0

    # scan through deck
    while i <= n - 3:
        window = deck_bits[i:i+3]
        if window == p1_seq:
            p1_tricks += 1
            p1_cards += (i + 3)   # count cards used
            deck_bits = deck_bits[i+3:]  # shorten deck
            n = len(deck_bits)
            i = 0
            continue
        elif window == p2_seq:
            p2_tricks += 1
            p2_cards += (i + 3)
            deck_bits = deck_bits[i+3:]
            n = len(deck_bits)
            i = 0
            continue
        i += 1

    # check draws
    draws_tricks = 1 if p1_tricks == p2_tricks else 0
    draws_cards = 1 if p1_cards == p2_cards else 0

    return p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards


def main():
    # load progress state
    progress = load_progress()
    matchup_index = progress["matchup_index"]
    file_index = progress["file_index"]

    # locate deck file
    deck_file = os.path.join(DECKS_DIR, f"decks_seed{file_index+1:03d}.bin")
    if not Path(deck_file).exists():
        print(f"No more deck files to process at index {file_index}. Done!")
        return

    # start runtime + memory tracking
    start_time = time.perf_counter()
    tracemalloc.start()

    # read all decks in file
    decks = read_decks_from_file(deck_file)
    print(f"Processing file: {deck_file} with {len(decks)} decks...")

    # load past results
    results = load_results()

    # loop through all decks
    for deck_bits in decks:
        p1_seq, p2_seq = MATCHUPS[matchup_index]

        # play game
        p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards = play_deck(deck_bits, p1_seq, p2_seq)

        key = (p1_seq, p2_seq)
        # initialize if new matchup
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

        # update results
        results[key]["p1_tricks"] += p1_tricks
        results[key]["p2_tricks"] += p2_tricks
        results[key]["draws_tricks"] += draws_tricks
        results[key]["p1_cards"] += p1_cards
        results[key]["p2_cards"] += p2_cards
        results[key]["draws_cards"] += draws_cards
        results[key]["runs"] += 1

        # advance matchup
        matchup_index = (matchup_index + 1) % len(MATCHUPS)

    # save results after file
    save_results(results)

    # update progress for next run
    progress["matchup_index"] = matchup_index
    progress["file_index"] = file_index + 1
    save_progress(progress)

    # stop timer + memory
    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Finished file {file_index+1}. Next run will use file index {file_index+1}.")
    print(f"Runtime: {elapsed:.2f} seconds | Peak memory: {peak / (1024*1024):.2f} MB")


if __name__ == "__main__":
    main()
