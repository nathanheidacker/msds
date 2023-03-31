from msds.rust import starforce as _starforce


def starforce(
    start: int, end: int, lvl: int, n: int = 100_000, progress: bool = True
) -> list[tuple[int, int, int]]:
    return _starforce(start, end, lvl, n, progress)
