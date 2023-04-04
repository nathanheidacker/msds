from msds.rust import _starforce
from typing import Iterable, Literal
import numpy as np
from enum import Enum


class StarforceResult:
    def __init__(
        self, start: int, end: int, lvl: int, results: Iterable[tuple[int, int, int]]
    ) -> None:
        self.size = len(results)
        self.start = start
        self.end = end
        self.lvl = lvl
        self.costs = []
        self.taps = []
        self.booms = []
        for costs, taps, booms in results:
            self.costs.append(costs)
            self.taps.append(taps)
            self.booms.append(booms)

        self.costs = np.array(self.costs)
        self.taps = np.array(self.taps)
        self.booms = np.array(self.booms)

    def __str__(self) -> str:
        return f"<Starforce Result | {self.start} -> {self.end} | lvl{self.lvl} | n={self.size}>"

    def __repr__(self) -> str:
        return str(self)

    def plt(
        self, comparand: float, metric: Literal["costs", "taps", "booms"] = "costs"
    ) -> float:
        """
        Probability less than

        Using this StarforceResult as an approximation of a probabilisic distribution,
        returns the probability that a starforce (from the start to end of this
        specific result) will achieve a value LESS than the input comparand for
        the given metric.

        For example, plt(10, "booms") will return the probability that a
        starforce from self.start to self.end at self.lvl will be achieved with
        LESS than 10 booms

        Args:
            comparand: The comparison value
            metric: The values to measure the probability of

        Returns:
            The probability
        """
        match metric:
            case "costs":
                nums = self.costs
            case "taps":
                nums = self.taps
            case "booms":
                nums = self.booms

        return (nums < comparand).mean()

    def pgt(
        self, comparand: float, metric: Literal["costs", "taps", "booms"] = "costs"
    ) -> float:
        """
        Probability greater than

        Using this StarforceResult as an approximation of a probabilisic distribution,
        returns the probability that a starforce (from the start to end of this
        specific result) will achieve a value GREATER than the input comparand for
        the given metric.

        For example, plt(10, "booms") will return the probability that a
        starforce from self.start to self.end at self.lvl will be achieved with
        GREATER than 10 booms

        Args:
            comparand: The comparison value
            metric: The values to measure the probability of

        Returns:
            The probability
        """
        match metric:
            case "costs":
                nums = self.costs
            case "taps":
                nums = self.taps
            case "booms":
                nums = self.booms

        return (nums > comparand).mean()


def starforce(
    start: int, end: int, lvl: int, n: int = 100_000, progress: bool = True
) -> StarforceResult:
    if not end > start:
        raise ValueError(
            f"End value must be greater than the starting value, received {start=}, {end=}"
        )

    if not 0 <= lvl <= 200:
        raise ValueError(f"lvl must be in the domain {{0, 200}}, received {lvl=}")

    results = _starforce(start, end, lvl, n, progress)
    return StarforceResult(start, end, lvl, results)
