# imports
import random

# number of cards in a standard deck
CARDS_PER_DECK = 52

# use a passed-in RNG for reproducibility
def generate_deck(rng: random.Random) -> int:
    # generate one deck encoded as a 52-bit integer (0=black, 1=red)
    # ensure exactly 26 red and 26 black
    cards = [1] * 26 + [0] * 26 
    rng.shuffle(cards)

    v = 0
    for c in cards:
        v = (v << 1) | c
    return v

# decode a deck integer into a string of 0s and 1s rather than ints
def decode_deck(deck_val: int) -> str:
    # return a 52-character string
    return bin(deck_val)[2:].zfill(CARDS_PER_DECK)

# count the number of red cards in a deck - tells user results of a deck
def count_reds(deck_val: int) -> int:
    return deck_val.bit_count()
