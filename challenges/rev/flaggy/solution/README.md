# Flaggy

The hardware circuit is a programmable voltage divider, a boost circuit is used to drive N-channel FETs to select from banks of 4 low- and 4 high-side resistors.

Semiconductors can be identified through OSINT using an SMD marking database.

Using known plaintext it is possible to find which resistors are active for the characters 'c', 'r', 'e', 'w' and '{', assuming two decades of E12 series resistors one of the two combinations that will produce the correct flag can be found.
With three decades it is possible to find a false flag; `crew{qLwzNxwrRosia\[wk^^oJjekgbzn}`

A simulation of the circuit can be found here: https://tinyurl.com/22mmljc2
