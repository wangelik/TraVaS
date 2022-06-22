# import table
import numpy as np


# mean absolute error
def mean_abs(val_a, val_b):

    # typecasting
    val_a = np.array(list(val_a))
    val_b = np.array(list(val_b))

    # return result
    return np.mean(np.abs(val_a - val_b))
