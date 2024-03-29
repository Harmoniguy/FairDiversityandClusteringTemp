import typing
import typing as t
import sys
import numpy as np
import numpy.typing as npt

import time

import math


class Stopwatch:
    def __init__(self, name: t.AnyStr):
        """
        Creates a new stopwatch that has started timing

        :param name: the name of the first split
        """
        self.names = [name]
        self.times = [time.perf_counter()]

    def split(self, name) -> None:
        """
        Stop the previous split and start another one with the given name
        :param name: the name of the new split
        :return: None
        """
        self.names.append(name)
        self.times.append(time.perf_counter())

    def get_splits(self):
        """
        Provides all existing splits, including the currently running split
        :return: a list of strings, one per split
        """
        return self.names

    def _calc_deltas(self) -> t.List[float]:
        return [b - a for a, b in zip(self.times, self.times[1:])]

    def stop(self):
        """
        Stops the clock
        :return: a list of (split-name, delta-time) pairs for every segment created via "split" and creation
                 as well as the total time
        """
        self.times.append(time.perf_counter())
        return zip(self.names, self._calc_deltas()), self.times[-1] - self.times[0]

def calculate_dmin_dmax(points):
    '''
    Estimates dmin and dmax for a set of points.

    dmin - min(smallest distance in all dimensions)
    dmax - l2-norm(largest co-ordinate in each dimension)

    '''
    arr = np.array(points)
    
    max_values = np.max(arr, axis=0)
    sum_of_squares = np.sum(max_values ** 2)
    dmax = np.sqrt(sum_of_squares)
    print('[done calulating dmax]', dmax)


    # Assuming you have a NumPy array 'arr' with shape (n, m)
    n, m = arr.shape

    # Step 1: Break the array into m arrays of n x 1
    split_arrays = np.split(arr, m, axis=1)

    # Step 2: For each array, find unique values
    unique_arrays = [np.unique(sub_arr) for sub_arr in split_arrays]

    # Step 3: Calculate the pair-wise distances for each unique array
    pairwise_distances = [np.diff(unique_arr, axis=0) for unique_arr in unique_arrays]

    # Step 4: Find the minimum pair-wise distance for each unique array
    min_distances_per_array = [np.min(distances) for distances in pairwise_distances]

    # Step 5: Find the minimum among the minimum pair-wise distances
    dmin = np.min(min_distances_per_array)
    print('[done calulating dmin]', dmin)

    return dmin, dmax


def compute_diversity(points: npt.NDArray[np.float64]) -> float:
    from scipy.spatial import distance
    div = sys.float_info.max
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            div = min(div, distance.euclidean(points[i], points[j]))
    return div

def compute_maxmin_diversity(points : npt.NDArray[np.float64]) -> float:
    """
    Computes maxmin diversity of a set of points (the minimum distance between any two points)
    under the Euclidean metric
    :param points: the set of points to compute diversity for
    :return: the minimum distance between points in points
    """
    from scipy.spatial import KDTree

    # get nearest point to each element
    tree = KDTree(points)
    distances, _ = tree.query(points, k=2)
    nonzero_distances = distances[:, 1]

    return np.min(nonzero_distances)


def buildKisMap(colors, k, a, equal_k_js = False):
    """
    builds a map to select at least (1-a) * k total points, spaced out in all colors
    The amount per color is calculated via the formula:
        max(1, (1-a) * k n_c / n)

    :param colors: an array of every color of the points in the dataset
    :param k: total # to select
    :param a: minimum percentage of k to allow
    :return: a map of unique colors to counts
    """
    N = len(colors)

    color_names, color_counts = np.unique(colors, return_counts=True)

    # we build up a dictionary of kis based on the names and counts
    # groups are built by the formula  max(1, (1-a) * k n_c / n)
    def calcKi(a, k, c):
        raw = max(1, ((1.0 - a) * k * c) / N)
        return math.ceil(raw)

    kis = {n: calcKi(a, k, c) for n, c in zip(color_names, color_counts)}

    if equal_k_js:
        return buildKisMap_equal(colors, k)

    return kis


def buildKisMap_equal(colors, k):
    """
    builds a map to build constraints of k/m points per color

    :param colors: an array of every color of the points in the dataset
    :param k: total # to select
    :return: a map of unique colors to counts
    """
    N = len(colors)

    color_names, color_counts = np.unique(colors, return_counts=True)

    # number of colors
    m = len(color_names)

    # number of points per color
    k_j = int(math.ceil(k/m))

    kis = {n: k_j for n in color_names}

    return kis

def check_returned_kis(colors, kis, S):
    """
    Computes the differences between each color value and chosen colors
    :param colors: the colors in the dataset
    :param kis: requested count per color
    :param S: computed solution (indicies into features and colors arrays)
    :return: a map of color to delta between kis and S
    """
    sol_colors = colors[S]

    color_vals, color_counts = np.unique(sol_colors, return_counts=True)

    # if we didn't return a color, our delta is the inverse of the requested count
    deltas = {c: -1 * count for c, count in kis.items()}

    # otherwise, we can compute the difference
    for color, computed in zip(color_vals, color_counts):
        actual = kis[color]
        delta = computed - actual
        deltas[color] = delta

    # we better have every color here
    assert (len(deltas.keys()) == len(kis.keys()))
    return deltas

def get_solution_kis(colors, S):
    """
    Computes the differences between each color value and chosen colors
    :param colors: the colors in the dataset
    :param kis: requested count per color
    :param S: computed solution (indicies into features and colors arrays)
    :return: a map of color to delta between kis and S
    """
    sol_colors = colors[S]

    color_vals, color_counts = np.unique(sol_colors, return_counts=True)

    kis_returned = {color: computed for color, computed in zip(color_vals, color_counts)}

    return kis_returned
