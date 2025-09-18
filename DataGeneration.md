**Files:**

method1.py : 
200 .bin files generated in decks_chunks with 10,000 random decks each. For each deck 52 bits (1 representing Red cards and 0 representing Black cards) are converted into 7 bytes.
Included in this script is code for generation and storage of decks and reading the files. (Note: files of 10,000 decks were used to break data into smaller replicable chunks and for consistency with method 2 which can fit fewer decks into one “github-supported” file.)

run_tests_method1.py: 
Runs the card generation and read code 10 times to get metrics (memory, generation time, write time, read time).. Prints metrics out in a table including results from each run and the means and standard deviations. 

decks_chunks: 
method 1 decks 

method2.py: 
200 .txt files are created with 10,000 random decks of cards in each file (stored in deck_chunks 2). Each deck is stored as a string of 0s and 1s with 0s for black cards and 1s for reds. Functions are here but are not called unless you run run_tests_method2.py script. 

run_tests_method2.py: 
Runs the card generations and measures and prints the time it takes to generate, read, and write the decks. Also measures and prints the memory all 2,000,000 decks take up. 

deck_chunks 2:
Method 2 decks 

 

**Metrics**

| Metric                   | Method 1: bits -> bytes -> bin files | Method 2: String -> .txt files |
|---------------------------|--------------------------------------|--------------------------------|
| Gen time mean (10 runs)   | 95.91 s                              | 94.780 s                        |
| Gen time std (10 runs)    | 1.81 s                               | 1.11 s                          |
| Read time mean (10 runs)  | 3.79 s                               | 1.658 s                         |
| Read time std (10 runs)   | 0.08 s                               | 0.037 s                         |
| Write time mean (10 runs) | 1.37 s                               | 3.324 s                         |
| Write time std (10 runs)  | 0.03 s                               | 0.027 s                         |
| Total memory use          | 13.35 MB                             | 103.00 MB  

**Write-Up**

We are choosing to use Method 1. The pros for method 1 include a shorter write and read time and less memory used for deck storage. The major con is that the data is stored in a less intuitive format. When you open the .bin files they appear to be a sprawl of random characters as the decks are stored in binary. Additionally, in order to search the decks they need to be converted (which is done in the read test). This may lead to some complications down the line in searching for sequences - however we believe this will be a fun challenge for us to figure out. Therefore we are prioritizing generation time and memory usage to drive our choice to select method 1. If we end up needing to generate more than 2 Million decks we can do this with reasonable runtime and low storage needs. 
