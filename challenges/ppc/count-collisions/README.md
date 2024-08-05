# Count-Collisions (10 solves)

I created this new weird hash function and hashed my message, but now I don't remember my message. How much work do I have to do to find my message?

# Writeup

This hash function picks an array and returns it sum, and the sum if we replaced the i-th sign of + with a XOR.

If we subtract the i-th value from the first value, the answer will be:

$ x_i + x_{i+1} - ( x_i \oplus x_{i+1} )  = 2 (x_i  x_{i+1})$. 

