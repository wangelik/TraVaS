# import table
import numpy as np
from dpv.util.converter import param_transform, merge
from dpv.data_utility import emd_utility, log_diff
from dpv.variant_transformer import private_transform


# optimizer for private multi queries
def release_optimizer(log, eps, delta, domain=[2, 10], avg=10, type='rel', clean=[False, False], data=False, debug=True):

    # init main containers
    util_results = dict()
    cost_results = dict()
    data_results = dict()
    splits = np.arange(min(domain), max(domain)+1)

    # investigate domain of subqueries
    for num in splits:

        # init temp containers
        util_avg = np.zeros(avg)
        cost_avg = np.zeros(avg)
        data_arr = []

        # repeat for averaging
        for a in range(avg):

            # init variant results
            traces_priv = [None] * num

            # convert to p and k
            p, k = param_transform(eps/num, delta/num)

            # run private subqueries
            for i in range(num):
                traces_orig, traces_priv[i] = private_transform(log, p, k)

            # merge sub logs
            traces_merged = merge(traces_priv, p, k)

            # save merged log
            if data is True:
                data_arr.append(traces_merged)

            # compute utility and absolute cost
            util_avg[a] = emd_utility(log, traces_merged)
            cost_avg[a] = log_diff(log, traces_merged)

            # create debug output
            if debug is True:
                print(f"[{a+1}] ({eps},{delta}) Split {num} | Util: {util_avg[a]} Cost: {cost_avg[a]}")

        # save cleaned average metrics and logs
        util_results[num] = np.mean([x for x in util_avg if x != clean[0]])
        cost_results[num] = np.mean([x for x in cost_avg if x != clean[1]])
        data_results[num] = data_arr

        # create debug output
        if debug is True:
            print(f"[*] ({eps},{delta}) Split {num} | Util: {util_results[num]} Cost: {cost_results[num]}")

    # optimize for relative utility
    if type == 'rel':
        mult = max(util_results, key=util_results.get)

    # optimize for absolute cost
    else:
        mult = min(cost_results, key=cost_results.get)

    # return results
    return util_results[mult], cost_results[mult], mult, util_results, cost_results, data_results[mult]
