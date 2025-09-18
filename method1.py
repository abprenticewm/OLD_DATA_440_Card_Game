#imports 
import os
import random
import time

#Params 
NUM_DECKS = 2_000_000   # total number of decks
DECK_SIZE_BITS = 52     # bits per deck
CHUNK_SIZE = 10_000     # number of decks per file picked 10k to match other method and because it is a smaller chunk that could be replicated
OUT_DIR = "decks_chunks"  # folder to save decks
BYTEORDER = "big"        # The most significant byte comes first

# do a check NUM_DECKS must be divisible by CHUNK_SIZE and figure out how many chunks we need
assert NUM_DECKS % CHUNK_SIZE == 0
NUM_CHUNKS = NUM_DECKS // CHUNK_SIZE  
BYTES_PER_DECK = (DECK_SIZE_BITS + 7) // 8


def generate_balanced_deck(rng: random.Random) -> bytes:
    """
    Generate a single deck with exactly 26 zeros and 26 ones,
    return as bytes.
    """
    bits = [0] * 26 + [1] * 26
    rng.shuffle(bits)  # shuffle to randomize order

    # Pack bits into an integer (bit shift and OR each value)
    #this part takes awhile unfortunatly - originally i just generated a length of 52 random bits which was SUPER fast
    #but unfortunatly that did not give me 26 0 and 26 1 so I had to pivot 
    deck_int = 0
    for bit in bits:
        deck_int = (deck_int << 1) | bit

    # Convert integer into raw bytes (needed for binary writing)
    return deck_int.to_bytes(BYTES_PER_DECK, byteorder=BYTEORDER)


def generate_chunk(chunk_index: int, out_dir: str = OUT_DIR):
    """
    Generate one chunk of decks, write to disk
    return (path, gen_time, write_time).
    """
    seed = chunk_index + 1  # increase seed by one (for replicability)
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)  # make directory if not exists

    filename = f"decks_seed{seed:03d}.bin"  # filename includes seed 
    path = os.path.join(out_dir, filename)  # full file path 

    # Generate decks 
    gen_start = time.perf_counter()  # start generation time 
    # creates all decks - 52 bits per deck, converted to bytes 
    decks = [generate_balanced_deck(rng) for _ in range(CHUNK_SIZE)]
    gen_time = time.perf_counter() - gen_start  # final gen time 

    # Write decks
    write_start = time.perf_counter()  # start write time 
    with open(path, "wb") as f:  # wb means: w = overwrite if already exists, b = binary mode 
        f.writelines(decks)  # writes all decks into file 
    write_time = time.perf_counter() - write_start  # final write time 

    return path, gen_time, write_time


def generate_chunks(start_chunk: int = 0, num_chunks: int = NUM_CHUNKS, out_dir: str = OUT_DIR):
    """
    Generate all chunks starting from start_chunk
    """
    created = []  # file paths of everything created 
    # times start at zero 
    total_gen_time = 0.0
    total_write_time = 0.0

    for i in range(start_chunk, start_chunk + num_chunks):
        path, gen_time, write_time = generate_chunk(i, out_dir=out_dir)  # generate chunk (file)!
        created.append(path)
        # add times for total time 
        total_gen_time += gen_time
        total_write_time += write_time

    return created, total_gen_time, total_write_time


# do generation 
def run_generation():
    """
    Generate all decks and return stats
    """
    start_time = time.perf_counter()

    created_files, total_gen_time, total_write_time = generate_chunks(
        start_chunk=0, num_chunks=NUM_CHUNKS, out_dir=OUT_DIR
    )

    end_time = time.perf_counter()
    total_runtime = end_time - start_time  # total runtime 
    total_memory = sum(os.path.getsize(p) for p in created_files)  # memory used 

    # return all of the metrics 
    return {
        "files": created_files,
        "total_runtime": total_runtime,
        "generation_time": total_gen_time,
        "write_time": total_write_time,
        "total_memory": total_memory,
    }


# read time test 
def read_decks(created_files):
    """
    Read all decks back from disk and return runtime
    """
    start_time = time.perf_counter()

    for filename in created_files:
        with open(filename, "rb") as f:  # open in read binary mode
            while (chunk := f.read(BYTES_PER_DECK)):  # read each deck 
                deck_int = int.from_bytes(chunk, "big")  # raw bytes → integer 
                _ = format(deck_int, f"0{DECK_SIZE_BITS}b")  # into a 52-length binary string for easy searching later 

    runtime = time.perf_counter() - start_time
    return runtime  # runtime is the only metric to return 


# run it all once!
if __name__ == "__main__":
    stats = run_generation()
    read_time = read_decks(stats["files"])

    # print metrics 
    print(f"\nDone. Created {len(stats['files'])} files in '{OUT_DIR}'.")
    print(f"Total runtime: {stats['total_runtime']:.2f} seconds")
    print(f"  Generation time: {stats['generation_time']:.2f} seconds")
    print(f"  Write time: {stats['write_time']:.2f} seconds")
    print(f"Total file size: {stats['total_memory'] / (1024*1024):.2f} MB")
    print(f"Read time: {read_time:.2f} seconds")
