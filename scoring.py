import csv
import json
import os
from pathlib import Path

# ==============================
# CONFIG
# ==============================
DECKS_DIR = "decks_chunks"
RESULTS_FILE = "results.csv"
PROGRESS_FILE = "progress.json"

DECK_SIZE_BITS = 52
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8

# ==============================
# MATCHUPS
# ==============================
SEQUENCES = [
    "000", "001", "010", "011",
    "100", "101", "110", "111",
]

# all pairings without duplicates (no "000 vs 000")
MATCHUPS = [(p1, p2) for i, p1 in enumerate(SEQUENCES) for j, p2 in enumerate(SEQUENCES) if i != j]


# ==============================
# PROGRESS
# ==============================
def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"matchup_index": 0, "file_index": 0}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


# ==============================
# RESULTS
# ==============================
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


# ==============================
# DECK READING
# ==============================
def read_decks_from_file(filename):
    """Read one deck file (binary) and return list of 52-bit strings."""
    decks = []
    with open(filename, "rb") as f:
        while (chunk := f.read(BYTES_PER_DECK)):
            deck_int = int.from_bytes(chunk, "big")
            deck_bits = format(deck_int, f"0{DECK_SIZE_BITS}b")
            decks.append(deck_bits)
    return decks


# ==============================
# GAME LOGIC
# ==============================
def play_deck(deck_bits, p1_seq, p2_seq):
    """Play through a single deck and return winner stats."""
    i = 0
    n = len(deck_bits)
    p1_tricks = p2_tricks = 0
    p1_cards = p2_cards = 0

    while i <= n - 3:
        window = deck_bits[i:i+3]
        if window == p1_seq:
            p1_tricks += 1
            p1_cards += (i + 3)  # cards up to and including sequence
            deck_bits = deck_bits[i+3:]  # remove used cards
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

    draws_tricks = 0
    draws_cards = 0
    if p1_tricks == p2_tricks:
        draws_tricks = 1
    if p1_cards == p2_cards:
        draws_cards = 1

    return p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards


# ==============================
# MAIN
# ==============================
def main():
    progress = load_progress()
    matchup_index = progress["matchup_index"]
    file_index = progress["file_index"]

    # Get deck file
    deck_file = os.path.join(DECKS_DIR, f"decks_seed{file_index+1:03d}.bin")
    if not Path(deck_file).exists():
        print(f"No more deck files to process at index {file_index}. Done!")
        return

    decks = read_decks_from_file(deck_file)
    print(f"Processing file: {deck_file} with {len(decks)} decks...")

    # Load results
    results = load_results()

    # Run scoring
    for deck_bits in decks:
        p1_seq, p2_seq = MATCHUPS[matchup_index]

        p1_tricks, p2_tricks, draws_tricks, p1_cards, p2_cards, draws_cards = play_deck(deck_bits, p1_seq, p2_seq)

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

        # advance matchup
        matchup_index = (matchup_index + 1) % len(MATCHUPS)

    # Save updated results
    save_results(results)

    # Update progress
    progress["matchup_index"] = matchup_index
    progress["file_index"] = file_index + 1
    save_progress(progress)

    print(f"Finished file {file_index+1}. Next run will use file index {file_index+1}.")


if __name__ == "__main__":
    main()
