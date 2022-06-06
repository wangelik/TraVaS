
## Computational Complexity

$(\epsilon, \delta)$-DP *partition selection* is considerably more efficient and easier to implement than current state-of-the-art tree-based query methods. To support large scale applications of our *TraVaS* framework, we will briefly discuss the most important complexity considerations of all associated algorithms (see our paper).

In the preprocessing phase of both the *SQVR* core and the optimizer shell, an event log $L$ needs to be transformed into its aggregated simple form, holding only variant-frequency pairs $(\sigma_A, L_A(\sigma_A))$.
This operation can be described as a Group-By-Count query that consumes $\mathcal{O}(n)$ steps with $n$ being the number of cases in $L$. Although large input logs may lead to runtime bottlenecks, the aggregation must only be executed once independent of further privatization processes.
The *SQVR* core then requires i.i.d *k-TSGD* random samples and variant deletion checks for all $m$ unique variants of $L$. Hence, we face a separate maximum complexity of $\mathcal{O}(m)$ with each *SQVR* run.  
Eventually, our *TraVaS* optimizer calls $u-l$ *SQVR* instances, implicating a worst-case complexity of $\mathcal{O}(u^2 \cdot m)$ according to the *Gaussian* sum formula. In addition, the same number of steps are needed for all merging and mean operations to obtain the respective candidate logs.
Together with $u-l$ utility computations and the final argmax function, Algorithm 2 therefore runs with a cumulative complexity of $\mathcal{O}(u^2 \cdot m + n)$. Note, that the cost function might possess a larger complexity than the *TraVaS* body.

One compelling advantage of our algorithm design is that only the initial event log transformation represents a sequential task. All subsequent routines such as the sublog construction, the merging or the cost evaluation can be perfectly parallelized on multiple computing units. As a result, industrial applications may partially compensate large inputs by stronger technology backbones.
