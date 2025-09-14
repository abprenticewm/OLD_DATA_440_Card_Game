#METHOD 1 - SOPHIA CODE 

#STILL NEED TO ADD  - run tests multiple times, in a function, make table 

#200 M files of 10,000 decks each named decks_seed001 (001, 002, 003...)
#0s and 1s stored in bits packed into bytes 
#saved runtime and memory 

#a load data chunk that reads every file 
#counts occurances of abitrary "10101"
#saved runtime 

#imports 
import os
import random
import time
from typing import List

# params
NUM_DECKS = 2_000_000 # num of decks 
DECK_SIZE_BITS = 52 #deck size
CHUNK_SIZE = 10_000 #each file will have 10, 000 decks 
OUT_DIR = "decks_chunks"   # directory to store chunk files
BYTEORDER = "big"          # use "big" for readability when converting to ints

# checks to ensure no errors will occur 
assert NUM_DECKS % CHUNK_SIZE == 0, "NUM_DECKS must be divisible by CHUNK_SIZE"
NUM_CHUNKS = NUM_DECKS // CHUNK_SIZE
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8  # number of bytes to store each deck


def generate_chunk(chunk_index: int, out_dir: str = OUT_DIR) -> str:
    """
    Generate CHUNK_SIZE decks using random.Random(seed)
    where seed = (chunk_index+1).
    Write them to a binary file whose name includes the seed.
    Returns the path to the written file.
    """
    seed = chunk_index + 1 #increase seed by one so we can replicate for each file 
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"decks_seed{seed:03d}.bin" #files are named with seed 
    path = os.path.join(out_dir, filename)

    with open(path, "wb") as f:
        for _ in range(CHUNK_SIZE):
            bits = rng.getrandbits(DECK_SIZE_BITS)
            f.write(bits.to_bytes(BYTES_PER_DECK, byteorder=BYTEORDER)) #squish bits into bytes 
    return path

def generate_chunks(start_chunk: int = 0, num_chunks: int = NUM_CHUNKS, out_dir: str = OUT_DIR) -> List[str]:
    """
    Generate a sequence of chunk files.
    - start_chunk: index of first chunk to create (0-based)
    - num_chunks: how many chunks to write starting at start_chunk
    Returns list of created file paths.
    """
    created = []
    for i in range(start_chunk, start_chunk + num_chunks):
        seed = i + 1
        print(f"Generating chunk {i} with seed {seed} ...")
        p = generate_chunk(i, out_dir=out_dir)
        created.append(p)
    return created

#main!
if __name__ == "__main__":
    start_time = time.perf_counter() #track time 

    created_files = generate_chunks(start_chunk=0, num_chunks=NUM_CHUNKS, out_dir=OUT_DIR)

    end_time = time.perf_counter()
    method1_runtime = end_time - start_time

    method1_memory = sum(os.path.getsize(p) for p in created_files)

    print(f"Done. Created {len(created_files)} files in '{OUT_DIR}'.")
    print(f"Runtime: {method1_runtime:.2f} seconds")


#read code

search_sequence = "10101" #an arbitrary sequence to test our data reading 
method2_matches = 0 #a count of this arbitrary sequence 

start_time = time.time()

for filename in created_files:  # uses files from earlier
    with open(filename, "rb") as f:
        while (chunk := f.read(BYTES_PER_DECK)):
            deck_int = int.from_bytes(chunk, "big")
            deck_str = format(deck_int, f"0{DECK_SIZE_BITS}b")  # 52-bit binary string
            if search_sequence in deck_str:
                method2_matches += 1
                # only count once per deck
                # so we break out of reading more from this deck
                # but since we're reading deck by deck, continue to next
                # (no inner loop here, so just continue naturally)

method2_runtime = time.time() - start_time

print(f"Search completed in {method2_runtime:.2f} seconds.")
print(f"Number of decks containing {search_sequence}: {method2_matches}")

