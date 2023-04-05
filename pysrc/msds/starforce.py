from msds.rust import _starforce, _starforce_mt
from typing import Iterable, Literal
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt


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
        return f"<Starforce Result | {self.start} -> {self.end} | lvl{self.lvl} | n={self.size:,}>"

    def __repr__(self) -> str:
        return str(self)

    def get_metric(self, metric: Literal["costs", "taps", "booms"]) -> np.ndarray:
        match metric:
            case "costs":
                return self.costs
            case "taps":
                return self.taps
            case "booms":
                return self.booms

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
        return (self.get_metric(metric) < comparand).mean()

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
        return (self.get_metric(metric) > comparand).mean()

    def histogram(
        self,
        metric: Literal["costs", "taps", "booms"],
        bins: int = 1000,
    ) -> None:
        """Displays a histogram of the input metric"""
        nums = self.get_metric(metric)
        metric_max = nums.max()
        metric_min = nums.min()
        metric_range = metric_max - metric_min
        if bins > metric_range:
            bins = int(metric_range)
        plt.hist(nums, bins=bins)
        plt.show()


def starforce(
    start: int,
    end: int,
    lvl: int,
    n: int = 100_000,
    multithreaded: bool = True,
    progress: bool = True,
) -> StarforceResult:
    """
    Performs starforce random walk n times

    Given a start, end, level, and number of iterations to perform, performs a
    Starforce random walk to completion for n iterations and returns the result
    as a StarforceResult, which allows for probability testing

    Args:
        start: Starting starforce level
        end: Desired end starforce level
        lvl: item level (??? not sure not a maplestory player)
        n: Number of iterations to perform
        progress: Whether or not to display a progress bar. Defaults to True

    Returns:
        StarforceResult
    """
    if not end > start:
        raise ValueError(
            f"End value must be greater than the starting value, received {start=}, {end=}"
        )

    if not 0 <= lvl <= 200:
        raise ValueError(f"lvl must be in the domain {{0, 200}}, received {lvl=}")

    sf = _starforce_mt if multithreaded else _starforce
    results = sf(start, end, lvl, n, progress)
    return StarforceResult(start, end, lvl, results)
