import itertools
import sys
import time
from typing import Any, Callable, List, Union

import networkx as nx
import numpy as np
from scipy.special import comb
import math
import algorithms.utilsfdm as utilsfdm
import random

import algorithms.fdmalgs_original as FDMO

ElemList = Union[List[utilsfdm.Elem], List[utilsfdm.ElemSparse]]

def FMMDS(features, colors, kis, epsilon, normalize=False):
    '''
    A wrapper for FairFlow
    Adjust the problem instance for a different set of parameters
    '''
    
    # number of colors
    c = len(kis)

    # size of final subset
    k = 0
    for ki in kis:
        k += kis[ki]


    # Create a map of indices to colors
    color_number_map = list(kis.keys())

    color_counts = {}
    for i in colors:
        if i not in color_counts:
            color_counts[i] = 1
        else:
            color_counts[i] += 1

    # As done in the paper we will pre-process the data
    # by normalizing to have zero mean and unit standard deviation.
    features = np.array(features)
    features_normalized = features.copy()
    mean = np.mean(features_normalized, axis=0)
    std = np.std(features_normalized, axis=0)
    features_normalized = features_normalized - mean
    features_normalized = features_normalized/std
    features = features.tolist()
    features_normalized = features_normalized.tolist()

    elements = []
    elements_normalized = []
    for i in range(0, len(features_normalized)):
        elem_normalized = utilsfdm.Elem(i, color_number_map.index(colors[i]), features_normalized[i])
        elem = utilsfdm.Elem(i, color_number_map.index(colors[i]), features[i])
        elements.append(elem)
        elements_normalized.append(elem_normalized)

    # Adjust the constraints as a list
    kis_list = []
    for color in color_number_map:
        kis_list.append(kis[color])

    # Adjust the constraints per color to as a range
    # +- offset for the values of kis
    # NOTE: The constraint for a single color in FMMD-S consists of a range [a, b]
    # where as the problem we study takes in constraint as [a, infinity].
    # To asjudt the constaints, we will set b = no. of points of that color
    c_offset = 5
    constr = []
    for color in color_number_map:
        range_constr = [kis[color], color_counts[color]]
        constr.append(range_constr)
    
    if normalize:
        return FDMO.scalable_fmmd_ILP(V=elements_normalized, k=k, EPS=epsilon, C=c,constr=constr ,dist=utilsfdm.euclidean_dist)
    else:
        return FDMO.scalable_fmmd_ILP(V=elements, k=k, EPS=epsilon, C=c,constr=constr ,dist=utilsfdm.euclidean_dist)