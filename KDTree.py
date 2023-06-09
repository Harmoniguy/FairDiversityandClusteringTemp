from sklearn.neighbors import KDTree
import numpy as np
import numpy.typing as npt


def create(points):
    """
    Creates a KDTree data structure over the "points"
    :param points: NP Array of features
    :return: KDTree of the features
    """
    return KDTree(points)


def get_ind(structure, r: np.float64, point) -> npt.NDArray[int]:
    """
    Queries the KDTree for neighbors within a radius r of point
    :param structure: KDTree to query over
    :param r: radius
    :param point: a point to query
    :return: a NPArray of indices
    """
    dim = point.shape[0]  # this is a tuple (reasons!)
    point_reshaped = np.reshape(point, (1, dim))

    return structure.query_radius(point_reshaped, r).flatten()[0]
