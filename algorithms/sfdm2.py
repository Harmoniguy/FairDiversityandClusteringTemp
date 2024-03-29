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

def StreamFairDivMax2(features, colors, kis, epsilon, gammahigh, gammalow, normalize=False, streamtimes = False):
    '''
    A wrapper for StreamFairDivMax2
    Adjust the problem instance for a different set of parameters
    '''

    c = len(kis)

    # Create a map of indices to colors
    color_number_map = list(kis.keys())

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
    
    if normalize:
        sol, sol_div, stream_time, post_time, total_time = FDMO.StreamFairDivMax2(
                                X=elements_normalized, 
                                k=kis_list, 
                                m=c,
                                dist=utilsfdm.euclidean_dist,
                                eps=epsilon,
                                dmax=gammahigh,
                                dmin=gammalow,
                            )
    else:
        sol, sol_div, stream_time, post_time, total_time = FDMO.StreamFairDivMax2(
                                X=elements, 
                                k=kis_list, 
                                m=c,
                                dist=utilsfdm.euclidean_dist,
                                eps=epsilon,
                                dmax=gammahigh,
                                dmin=gammalow,
                            )
        
    if streamtimes:
        # print(f'[SFDM2-Wrap] total stream time = {stream_time}')
        # print(f'[SFDM2-Wrap] post time = {post_time}')
        # print(f'[SFDM2-Wrap] total time = {total_time}')
        return np.array(list(sol)), sol_div, [stream_time, post_time, total_time]
    else:
        return np.array(list(sol)), sol_div, total_time