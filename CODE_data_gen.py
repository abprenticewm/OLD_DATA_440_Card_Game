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


def generate_chunk(chunk_index: int, num_decks: int = CHUNK_SIZE, out_dir: str = OUT_DIR):
    """
    Create a deck chunk file containing num_decks decks.
    If the file already exists, skip creation.
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
        for _ in range(num_decks):
            f.write(generate_balanced_deck(rng))

    print(f"Created file ({num_decks} decks): {filename}")
    return path


def get_existing_chunks(out_dir: str = OUT_DIR) -> int:
    """
    Count how many deck files currently exist in the output directory.
    """
    if not os.path.exists(out_dir):
        return 0
    return len([f for f in os.listdir(out_dir) if f.startswith("decks_seed") and f.endswith(".bin")])


def generate_decks(n_new: int, out_dir: str = OUT_DIR):
    """
    Generate the requested number of new decks.
    Creates full 10k chunks and a final smaller chunk if needed.
    """
    os.makedirs(out_dir, exist_ok=True)
    existing = get_existing_chunks(out_dir)

    num_full_chunks = n_new // CHUNK_SIZE
    remainder = n_new % CHUNK_SIZE
    generated_files = []

    # Create full chunks
    for i in range(num_full_chunks):
        path = generate_chunk(existing + i, CHUNK_SIZE, out_dir)
        if path:
            generated_files.append(path)

    # Create final chunk if needed
    if remainder > 0:
        path = generate_chunk(existing + num_full_chunks, remainder, out_dir)
        if path:
            generated_files.append(path)

    print(f"Generated {n_new} decks across {len(generated_files)} file(s).")
    return generated_files


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate binary deck chunk files.")
    parser.add_argument("num_decks", type=int, help="Number of decks to generate")
    args = parser.parse_args()

    generate_decks(args.num_decks)
