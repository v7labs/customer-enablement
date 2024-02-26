import numpy as np


def Array_AND(arr1, arr2):
    """
    A function that takes two multidimensional arrays (with the same dimensions) and returns an array where each component has undergone AND logic
    """
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)

    flat_1 = Flatten(arr1)
    flat_2 = Flatten(arr2)

    and_array = np.logical_and(flat_1, flat_2)
    count_and_array = np.count_nonzero(and_array)

    return and_array, count_and_array


def Array_OR(arr1, arr2):
    """
    A function that takes two multidimensional arrays (with the same dimensions) and returns an array where each component has undergone OR logic
    """
    arr1 = np.array(arr1)
    arr2 = np.array(arr2)

    flat_1 = Flatten(arr1)
    flat_2 = Flatten(arr2)

    or_array = np.logical_or(flat_1, flat_2)
    count_or_array = np.count_nonzero(or_array)

    return or_array, count_or_array


def Flatten(arr):
    """
    Returns a flattened array
    """
    return arr.flatten()


def Max_Array_Count(arr1, arr2):
    """
    Returns the max count for two binary arrays
    """
    narr1 = np.array(arr1)
    narr2 = np.array(arr2)

    counts1 = np.count_nonzero(narr1)
    counts2 = np.count_nonzero(narr2)

    return max(counts1, counts2)


def Array_Count(arr1):
    """
    Returns the non-zero count for an array
    """
    narr1 = np.array(arr1)
    counts1 = np.count_nonzero(narr1)
    return counts1
