# import table
import numpy as np

# general settings
GS_SCORE = 1  # score has sensitivity of 1


# exp score function
def score(output_universes):
    return [x for x in np.flip(output_universes)]


# apply exp noise mechanism
def exp_mech(output_universes, epsilon):

    scores = score(output_universes)
    raw_prob = [np.exp((epsilon * x) / (2 * GS_SCORE)) for x in scores]
    max_value = np.sum(raw_prob)
    prob = [x / max_value for x in raw_prob]
    
    return np.random.choice(output_universes, p=prob)
