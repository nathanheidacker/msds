from __future__ import annotations
from msds.rust import _starforce, _starforce_mt
from typing import Iterable, Literal, Optional
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
from pathlib import Path


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
        self.ordered = False

    def __str__(self) -> str:
        return f"<Starforce Result | {self.start} -> {self.end} | lvl{self.lvl} | n={self.size:,}>"

    def __repr__(self) -> str:
        return str(self)

    def save(
        self, name: str, dir: Optional[str | Path] = None, overwrite: bool = True
    ) -> bool:
        """Saves a StarforceResult so that it may be instantiated quickly"""
        ...

    def load(self, name: str, dir: Optional[str | Path] = None) -> StarforceResult:
        """Loads a StarforceResult from persistent storage"""
        ...

    def order(self) -> None:
        """Sorts all results an ascending order"""
        if not self.ordered:
            self.costs.sort()
            self.taps.sort()
            self.booms.sort()
            self.ordered = True

    def percentile(
        self, percentile: float, metric: Literal["costs", "taps", "booms"]
    ) -> int:
        """
        Returns the value of the input percentile for the given metric

        Given an input percentile value between 0 and 1, returns the value of
        that percentile within the input metric.

        Args:
            percentile: The percentile value to find within the metric
            metric: The metric within which to search for the given percentile

        Returns:
            The value of the metric at the given percentile
        """
        if not 0 <= percentile <= 1:
            raise ValueError(
                f"Percentile must be between 0 and 1, recieved {percentile=}"
            )

        self.order()
        nums = self.get_metric(metric)
        idx = min(int(self.size * percentile), self.size - 1)
        return nums[idx]

    def get_percentile(
        self, value: float, metric: Literal["costs", "taps", "booms"]
    ) -> float:
        """
        Returns the percentile of a given value for a given metric

        Given some value, returns the percentile of that value within the input
        metric

        Args:
            value: The value to find the percentile of
            metric: The metric to search within

        Returns:
            The percentile, a value ranging between 0 and 1
        """
        self.order()
        nums = self.get_metric(metric)
        return 0

    def get_metric(self, metric: Literal["costs", "taps", "booms"]) -> np.ndarray:
        match metric:
            case "costs":
                return self.costs
            case "taps":
                return self.taps
            case "booms":
                return self.booms
        raise ValueError(
            f"Invalid metric '{metric}'. Please use one of 'costs', 'taps', or 'booms'"
        )

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

    def overview(self) -> None:
        self.order()
        max_cost = len(f"{self.costs[-1]:,}")
        max_taps = len(str(self.taps[-1]))
        max_booms = len(str(self.booms[-1]))
        header = str(self)
        overview = f"{header}\nPERCENTILES\n-----------\n"
        values = [*range(0, 10), 9.5, 9.9]
        for i in values:
            i /= 10
            costs, taps, booms = [
                self.percentile(i, metric) for metric in ["costs", "taps", "booms"]
            ]

            percentile = str(int(i * 100))
            percentile_pad = " " * (3 - len(percentile))
            percentile = f"{percentile}%{percentile_pad}"

            costs = f"{costs:,}"
            costs_padding = " " * (max_cost - len(costs))
            costs = f"costs: {costs}{costs_padding}"

            taps = str(taps)
            taps_padding = " " * (max_taps - len(taps))
            taps = f"taps: {taps}{taps_padding}"

            booms = str(booms)
            booms_padding = " " * (max_booms - len(booms))
            booms = f"booms: {booms}{booms_padding}"

            overview += f"{percentile}| {costs}| {taps}| {booms}\n"

        return overview

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
