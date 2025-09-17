# imports
import random

# number of cards in a standard deck
CARDS_PER_DECK = 52

# use a passed-in RNG for reproducibility
def generate_deck(rng: random.Random) -> int:
    # generate one deck encoded as a 52-bit integer (0=black, 1=red)
    v = 0
    # add one random card at a time
    for _ in range(CARDS_PER_DECK):
        v = (v << 1) | rng.randint(0, 1)
    return v

# decode a deck integer into a string of '0'/'1' rather than ints
def decode_deck(deck_val: int) -> str:
    # return a 52-character string
    return bin(deck_val)[2:].zfill(CARDS_PER_DECK)

# count the number of red cards in a deck - tells user results of a deck
def count_reds(deck_val: int) -> int:
    return deck_val.bit_count()
