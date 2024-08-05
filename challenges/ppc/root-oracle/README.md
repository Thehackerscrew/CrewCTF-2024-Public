# Root-Oracle (13 solves)



# Writeup

We can make queries on the form i,j,k, where i,j,k are indices, and ask the number of real roots of $p_i * x^2+p_j * x+p_k=0$. We must find the hidden permutation of $1,2,\dots,n$.

This is equivalent of knowing the sign of $\delta=p_j ^2 -4*p_i * p_k$.

If we query a,b,a, we can check the sign of $p_{b}^2-4*p_{a}^2$, which is the the sign of $p_b-2*p_a$.

Thus, we can know the position of $1$ by doing this procedure repeatedly: Put all numbers on the set $S$, pick a random number $a$ from $S$ and then only keep the values $b$ for which querying $a,b,a$ gives 0 roots.
