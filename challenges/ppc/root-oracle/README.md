# Root-Oracle (11 solves)

Can you guess my secret permutation with only these weird queries?

# Writeup

We can make queries on the form i,j,k, where i,j,k are indices, and ask the number of real roots of $p_i  x^2+p_j  x+p_k=0$. We must find the hidden permutation of $1,2,\dots,n$.

This is equivalent of knowing the sign of $\delta=p_j ^2 -4 p_i  p_k$.

If we query a,b,a, we can check the sign of $p_b ^2 - 4 p_a ^2$, which is the the sign of $p_b-2 p_a$.

Thus, we can know the position of $1$ by doing this procedure repeatedly: Put all numbers on the set $S$, pick a random number $a$ from $S$ and then only keep the values $b$ for which querying $a,b,a$ gives 0 roots. This procedure in expectation does $O(n)$ queries.

After obtaining the position of all numbers up to $X$, we can use induction to obtain all positions up to $2X$ in $O(N+Xlog(X))$ queries.

Let $inv_x$ denote the position of $x$.

Then, we can ask $inv_X,i,inv_X$ for every number to know if they are less than $2X$. Then, we can use binary search for each of these numbers to find an integer A such that $A \leq \frac{p_i}{2} < A+1$, and with by querying $inv_A,p_i,inv_A$ we know the parity of $p_i$. Thus, we use $O(log(X))$ queries for each value, and thus the number of total queries is $O(Nlog(N))$.



