# TraVaS
This repository provides the codebase and all experimental results of the publication
"TraVaS: Differentially Private Trace Variant Selection for Process Mining" (Wangelik et al.).  
For the experiments three event logs (BPIC2012App, BPIC2013, Sepsis) were anonymized by two
$(\epsilon, \delta)$-DP methods of TraVaS (single query, multi query) and a benchmark (tree-based query [1]). 
The private logs have then been evaluated against two data utility measures (log distribution difference, absolute difference cost) and three result utility functions (log fitness, precision, generalization).
Due to the underlying probabilistic nature, each privacy parameter combination was executed 10 times in order to average result metrics.  
More detailed information can be found in the respective document.

## Structure
The data is structured as follows. For each event log a specific folder within `experiments` contains:
* the original XES log file
* a `run.ipynb` jupyter notebook (to recreate all data and graphics)
* three folders `single`, `multi` and `benchmark` (data folders)
* the two final plots (data utility and result utility)

The folders `single`, `multi` and `benchmark` refer to the anonymization methods `TraVaS SQVR`, `TraVaS Optimizer` and a tree-based iterative query engine respectively [1]. They contain two types of files:
* variants_[*method*]\_[*epsilon*]\_[*delta*]_[*repetition*].json (privatized log)
* [*measure*]_[*method*].txt (averaged evaluation data for all $(\epsilon, \delta)$ combinations)

## Notes
In particular the data utility metrics can be computationally expensive to compute. Hence we advise to ensure sufficient CPU- and memory resources.  
Any feedback is expected to arrive at `frederik.wangelik@rwth-aachen.de`

## Literature

[1] Mannhardt, F., Koschmider, A., Baracaldo, N. et al.: Privacy-Preserving Process Mining. Bus. Inf. Syst. Eng. 61, 595–614 (2019).