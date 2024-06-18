import pandas as pd
import numpy as np

def locate_edges(binary_sequence):
    """
    Find the positions of leading and falling edges in a binary sequence and
    report the onsets and durations of associated events.

    :param binary_sequence: a sequence of 0s and 1s (int)
    :return: two lists of integers corresponding to indices of raising and falling edges
    """
    if isinstance(binary_sequence, (list, pd.core.series.Series)):
        binary_sequence = np.array(binary_sequence)
    if len(binary_sequence) <= 2:
        return None, None
    assert binary_sequence[
        0] == 0  # check that the signal is at baseline when starting
    assert binary_sequence[
        -1] == 0  # check that the signal returned to baseline at the end
    leading_edges = 1 + np.flatnonzero((binary_sequence[:-1] == 0)
                                       & (binary_sequence[1:] == 1))
    falling_edges = 1 + np.flatnonzero((binary_sequence[:-1] == 1)
                                       & (binary_sequence[1:] == 0))
    return leading_edges, falling_edges
