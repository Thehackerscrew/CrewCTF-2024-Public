# Count-Collisions (10 solves)

I created this new weird hash function and hashed my message, but now I don't remember my message. How much work do I have to do to find my message?

# Writeup

This hash function picks an array and returns it sum, and the sum if we replaced the i-th sign of + with a XOR.

If we subtract the i-th value from the first value, the answer will be:

$x_i+x_{i+1}-x_i \oplus x_{i+1}=2 (x_i AND x_{i+1})$.

Thus, we can know the bitwise AND of any two consecutive values.

With that, we can resort to dynamic programming: We can calculate, for the $j$-th bit, the number of ways we can set exactly $k$ of these bits to one, since every "row" of bits is independent. Let's denote that by $CNT_{j,k}$.

Then, we denote $DP_{pos,carry}$ to be the number of ways to set all the bits up to $pos$, in such a way that adding all $x_i$ generates a carry of $carry$.

Thus, we can try to add all the possible number of ones in the row of $pos$ and update the carry accordingly, in such a way that the final sum does coicide with the known sum.

This DP runs in $O(m n^2)$ operations.



