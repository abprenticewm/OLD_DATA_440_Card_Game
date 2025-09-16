from method1 import run_generation, read_decks #import methods from main file 
import statistics #for calculations 

N_RUNS = 10 #to make sure data is generlized, may change this number 


def run_tests():
    '''
    Generate decks and get read time N times.
    Save stats on read and write times and memory.
    '''
    results = [] #array of all stats 

    for i in range(N_RUNS):
        #run the code 
        stats = run_generation()
        read_time = read_decks(stats["files"])

        #save the stats 
        run_stats = {
            "runtime": stats["total_runtime"],
            "generation": stats["generation_time"],
            "write": stats["write_time"],
            "memory_mb": stats["total_memory"] / (1024 * 1024),
            "read": read_time,
        }
        results.append(run_stats)

        print(f"Run {i+1}/{N_RUNS} completed.") #update screen as runs are completed 

    return results


def print_results(results):
    '''
    Print table with results. 
    Is a new method for clarity. 
    '''
    # Print header
    print("\nResults per run:")
    print(f"{'Run':>3} | {'Runtime(s)':>10} | {'Gen(s)':>8} | {'Write(s)':>8} | {'Read(s)':>8} | {'Mem(MB)':>8}") #space it out nicely 
    print("-" * 60) #line for clarity 

    #print info from each run 
    for i, r in enumerate(results, start=1):
        print(f"{i:>3} | {r['runtime']:>10.2f} | {r['generation']:>8.2f} | "
              f"{r['write']:>8.2f} | {r['read']:>8.2f} | {r['memory_mb']:>8.2f}")

    #compute means and sd
    keys = ["runtime", "generation", "write", "read", "memory_mb"]
    print("-" * 60)
    print(f"{'AVG':>3} | " + " | ".join(f"{statistics.mean([r[k] for r in results]):>8.2f}" for k in keys))
    print(f"{'STD':>3} | " + " | ".join(f"{statistics.stdev([r[k] for r in results]):>8.2f}" for k in keys))

#run it all!
if __name__ == "__main__":
    results = run_tests()
    print_results(results)
