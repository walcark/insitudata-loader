"""
pipeline.py

Author  : Kévin Walcarius
Date    : 2025-01-16
Version : 1.0
License : MIT
Summary : Method that allow to chain other methods.
"""

from __future__ import annotations

from typing import Callable, Generic, TypeVar

T = TypeVar("T")
Step = Callable[[T], T]


class Pipeline(Generic[T]):
    """
    Chains steps (callables) of signature `T -> T`.

    Parameters
    ----------
    *steps:
        Unnamed steps, executed in order.
    keep_intermediate_values:
        If True, stores intermediate outputs in `last_intermediate`.
    **named_steps:
        Named steps, appended after positional steps (keeps insertion order).
    """

    def __init__(
        self,
        *steps: Step[T],
        keep_intermediate_values: bool = False,
        **named_steps: Step[T],
    ) -> None:
        self.keep_intermediate_values = keep_intermediate_values
        self.last_intermediate: dict[str, T] = {}

        self._steps: list[tuple[str, Step[T]]] = [
            (f"Step {i}", step) for i, step in enumerate(steps, start=1)
        ]
        self._steps += list(named_steps.items())

    def __call__(self, x: T) -> T:
        self.last_intermediate.clear()

        val = x
        for name, fn in self._steps:
            val = fn(val)
            if self.keep_intermediate_values:
                self.last_intermediate[name] = val

        return val
