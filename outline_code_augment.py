'''
MAIN

import time
from data_gen import generate_decks
from scoring import score_all_files


def augment_data():
    """
    Ask the user how many decks to generate, run data generation,
    then score all available decks and update the results file.
    """
    try:
        n = int(input("How many new decks would you like to generate? "))
        if n <= 0:
            print("Please enter a positive number.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    print(f"Generating {n} new decks...")
    start_time = time.perf_counter()
    new_files = generate_decks(n)
    gen_time = time.perf_counter() - start_time
    print(f"Deck generation completed in {gen_time:.2f} seconds.\n")

    print("Scoring new deck files...")
    start_score = time.perf_counter()
    score_all_files()
    score_time = time.perf_counter() - start_score
    print(f"Scoring completed in {score_time:.2f} seconds.\n")

    print("Augmentation complete. All data and results are up to date.")


if __name__ == "__main__":
    print("Deck Data Augmentation Tool")
    augment_data()

    

    
SCORING 

import os
import csv

# Default configuration
DECKS_DIR = "data/decks_chunks"
RESULTS_FILE = "data/results.csv"
DECK_SIZE_BITS = 52
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8


def score_deck(deck_bytes: bytes) -> float:
    """
    Compute a simple score for one deck.
    Example metric: fraction of bits set to 1.
    Replace with custom scoring logic as needed.
    """
    bit_count = sum(bin(byte).count("1") for byte in deck_bytes)
    return bit_count / DECK_SIZE_BITS


def score_file(file_path: str):
    """
    Read all decks from a binary file and return their scores.
    Supports both full and partial (smaller) deck files.
    """
    scores = []
    with open(file_path, "rb") as f:
        data = f.read()

    num_decks = len(data) // BYTES_PER_DECK

    for i in range(num_decks):
        start = i * BYTES_PER_DECK
        end = start + BYTES_PER_DECK
        deck_bytes = data[start:end]
        scores.append(score_deck(deck_bytes))

    return scores


def score_all_files(decks_dir: str = DECKS_DIR, results_file: str = RESULTS_FILE):
    """
    Score all unprocessed deck files and append results to CSV.
    Already-scored files are skipped automatically.
    """
    if not os.path.exists(decks_dir):
        raise FileNotFoundError(f"Deck directory '{decks_dir}' not found.")

    files = sorted(f for f in os.listdir(decks_dir) if f.endswith(".bin"))

    # Track files already scored
    scored_files = set()
    if os.path.exists(results_file):
        with open(results_file, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                scored_files.add(row["file"])

    new_results = []
    for fname in files:
        if fname in scored_files:
            print(f"Skipping already scored file: {fname}")
            continue

        path = os.path.join(decks_dir, fname)
        scores = score_file(path)

        for i, s in enumerate(scores):
            new_results.append((fname, i, s))

        print(f"Scored {len(scores)} decks from {fname}")

    if not new_results:
        print("No new files to score.")
        return

    # Append to results.csv without overwriting
    file_exists = os.path.exists(results_file)
    with open(results_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["file", "deck_index", "score"])
        writer.writerows(new_results)

    print(f"Added {len(new_results)} new results to {results_file}.")

    

DATA GEN 

import os
import random
from pathlib import Path

# Default configuration
OUT_DIR = "data/decks_chunks"       # Directory where generated binary deck files are stored
CHUNK_SIZE = 10_000                 # Number of decks per full chunk file
DECK_SIZE_BITS = 52                 # Number of bits per deck
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8  # Convert bits to required bytes per deck


def generate_balanced_deck(rng: random.Random) -> bytes:
    """
    Create one balanced deck (equal 0s and 1s) and return as bytes.
    """
    bits = [0] * 26 + [1] * 26
    rng.shuffle(bits)

    deck_int = 0
    for bit in bits:
        deck_int = (deck_int << 1) | bit

    return deck_int.to_bytes(BYTES_PER_DECK, byteorder="big")


def generate_chunk(chunk_index: int, out_dir: str = OUT_DIR):
    """
    Create a full 10,000-deck binary file.
    Skips creation if the file already exists.
    """
    seed = chunk_index + 1
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"decks_seed{seed:03d}.bin"
    path = os.path.join(out_dir, filename)

    if os.path.exists(path):
        print(f"Skipping existing file: {filename}")
        return None

    with open(path, "wb") as f:
        for _ in range(CHUNK_SIZE):
            f.write(generate_balanced_deck(rng))

    print(f"Created full chunk: {filename}")
    return path


def generate_partial_chunk(num_decks: int, chunk_index: int, out_dir: str = OUT_DIR):
    """
    Create a smaller binary file with fewer than 10,000 decks.
    """
    seed = chunk_index + 1
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"decks_seed{seed:03d}_partial.bin"
    path = os.path.join(out_dir, filename)

    if os.path.exists(path):
        print(f"Skipping existing partial file: {filename}")
        return None

    with open(path, "wb") as f:
        for _ in range(num_decks):
            f.write(generate_balanced_deck(rng))

    print(f"Created partial file ({num_decks} decks): {filename}")
    return path


def get_existing_chunks(out_dir: str = OUT_DIR) -> int:
    """
    Count how many deck files currently exist in the output directory.
    Used to determine next available file index.
    """
    if not os.path.exists(out_dir):
        return 0
    return len([f for f in os.listdir(out_dir) if f.startswith("decks_seed") and f.endswith(".bin")])


def generate_decks(n_new: int, out_dir: str = OUT_DIR):
    """
    Generate the requested number of new decks.
    Creates multiple 10k chunks if needed and one smaller partial file for the remainder.
    """
    os.makedirs(out_dir, exist_ok=True)
    existing = get_existing_chunks(out_dir)

    num_full_chunks = n_new // CHUNK_SIZE
    remainder = n_new % CHUNK_SIZE
    generated_files = []

    # Create all full 10k chunks
    for i in range(num_full_chunks):
        path = generate_chunk(existing + i, out_dir)
        if path:
            generated_files.append(path)

    # Create smaller remainder file if needed
    if remainder > 0:
        path = generate_partial_chunk(remainder, existing + num_full_chunks, out_dir)
        if path:
            generated_files.append(path)

    print(f"Generated {n_new} decks across {len(generated_files)} file(s).")
    return generated_files



'''