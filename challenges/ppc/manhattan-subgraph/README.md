
A 4-cycle in the given graph always corresponds to a face of a cube.
In a 4-cycle, we also know that opposite edges have the same direction, and adjacent edges have different direction.
Thus, if we consider a graph where the vertices represent the edges of our original graph, we have a 3-coloring problem (where some edges represent same color and some different color) but given that the cubes are connected, we can always deduce the color of every edge using a DFS with two possible states:
- we know that the color of vertex x is y
- we know the color of adjacent vertices with different colors


Then, we propagate in O(n^3) and use one of the possible 6 solutions.
We also need to determine the exact vectors of each edge, which also can be done with a DFS given that we know the direction of each edge, in O(n^3). There are $2^3=8$ possibilities.
Finally, we can determine for every of the possible 6*8=48 solutions the positions of all vertices and then determine whether a cube is placed by examining if all its edges are present in the original graph, in O(n^3).
Test all 48 possibilities and use the one with the correct hash.
