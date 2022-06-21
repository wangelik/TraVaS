# TraVaS
This repository provides the codebase and all experimental results of the publication
"TraVaS: Differentially Private Trace Variant Selection for Process Mining" (Rafiei et al.).  
For the experiments three event logs (BPIC2012App, BPIC2013, Sepsis) were anonymized by two
(&epsilon;, &delta;)-DP methods of TraVaS (single query and multi query) and a benchmark [1] plus the extension of the benchmark (SaCoFa [2] - only for Sepsis as the most challenging event log). 
The private logs have then been evaluated against two data utility measures (relative log similarity and absolute log difference) and two result utility functions (log fitness, precision).
Due to the underlying probabilistic nature, each privacy parameter combination was executed 10 times in order to average result metrics.  
More detailed information can be found in the respective document.

## Structure
The data is structured as follows. For each event log a specific folder within `implementation & experiments` contains:
* the original XES log file
* a `run.ipynb` jupyter notebook (to recreate all data and graphics)
* three folders `single`, `multi` and `benchmark` (data folders)
* the two final plots (data utility and result utility)

The folders `single`, `multi` and `benchmark` refer to the anonymization methods `TraVaS SQVR`, `TraVaS Optimizer` and a tree-based iterative query engine respectively [1]. They contain two types of files:
* variants_[*method*]\_[*epsilon*]\_[*delta*]_[*repetition*].json (privatized log)
* [*measure*]_[*method*].txt (averaged evaluation data for all (&epsilon;, &delta;) combinations)

## Notes
In particular the data utility metrics can be computationally expensive to compute. Hence we advise to ensure sufficient CPU- and memory resources.  
Any feedback is expected to arrive at `frederik.wangelik@rwth-aachen.de`

## Literature

[1] Mannhardt, F., Koschmider, A., Baracaldo, N. et al.: "Privacy-Preserving Process Mining." Bus. Inf. Syst. Eng. 61, 595–614 (2019).

[2] Fahrenkog-Petersen, Stephan A., et al. "SaCoFa: Semantics-aware Control-flow Anonymization for Process Mining." 2021 3rd International Conference on Process Mining (ICPM). IEEE, (2021).