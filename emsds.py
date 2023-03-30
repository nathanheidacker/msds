import msds
from tqdm import tqdm
from time import perf_counter

if __name__ == "__main__":
    start = perf_counter()
    N = 1_000_000
    for _ in range(N):
        msds.starforce_single(15, 20, 150)
    t = perf_counter() - start
    print(f"{t:.04f} seconds to perform {N} iterations\n{N/t:.04f} iterations per second")