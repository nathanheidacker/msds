import msds
from tqdm import tqdm
from time import perf_counter

if __name__ == "__main__":
    N = 1_000_000

    start = perf_counter()
    for _ in range(N):
        msds.starforce_single(15, 21, 150)
    t = perf_counter() - start
    print(f"{t:.04f} seconds to perform {N} iterations\n{N/t:.04f} iterations per second")

    start = perf_counter()
    msds.starforce_benchmark(15, 21, 150, N)
    t = perf_counter() - start
    print(f"{t:.04f} seconds to perform {N} iterations\n{N/t:.04f} iterations per second")

    start = perf_counter()
    msds.starforce(15, 21, 150, N)
    t = perf_counter() - start
    print(f"{t:.04f} seconds to perform {N} iterations\n{N/t:.04f} iterations per second")