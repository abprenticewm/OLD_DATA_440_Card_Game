
**Files:**

method1.py : 
200 .bin files generated in decks_chunks with 10,000 random decks each. For each deck 52 bits (1 representing Red cards and 0 representing Black cards) are converted into 7 bytes.
Included in this script is code for generation and storage of decks and reading the files. 

run_tests_method1.py: 
Runs the card generation and read code 10 times to get metrics (memory, generation time, write time, read time).. Prints metrics out in a table including results from each run and the means and standard deviations. 

decks_chunks: 
method 1 decks 

method2.py: 
200 .txt files are created with 10,000 random decks of cards in each file (stored in deck_chunks 2). Each deck is stored as a string of 0s and 1s with 0s for black cards and 1s for reds. 

run_tests_method2.py: 
Runs the card generations and measures and prints the time it takes to generate, read, and write the decks. Also measures and prints the memory all 2,000,000 decks take up. 

deck_chunks 2:
Method 2 decks 

**Metrics**

| Metric                 | Method 1: bits -> bytes -> bin files | Method 2: String -> .txt files |
|-------------------------|--------------------------------------|--------------------------------|
| Gen time mean (10 runs) | 95.91s                               | 141.082s                       |
| Gen time std (10 runs)  | 1.81s                                | 4.515s                         |
| Read time mean (10 runs)| 3.79s                                | 10.074s                        |
| Read time std (10 runs) | 0.08s                                | 0.193s                         |
| Write time mean (10 runs)| 1.37s                               | 2.580s                         |
| Write time std (10 runs) | 0.03s                               | 0.080s                         |
| Total memory use        | 13.35MB                              | 103.00MB   

**Write-Up**
