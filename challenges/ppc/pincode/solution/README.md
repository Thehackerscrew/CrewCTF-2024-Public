# PINcode

The gif contains images which are supposed to resemble the digits on a swipe-to-unlock lock screen.
Each frame displays a single digit with the incoming and outgoing swipe angles for that digit.
From the set of digits and the set of angles present in the gif we can surmise that it's a 4x4 keypad.
The pin to bytes conversion is essentially base15, choosing from 16 digits with no repeats.

The provided solution extracts the angles from the image and calculates which PIN codes would be possible.
For some angles there is only one solution while others will be ambiguous. (Swiping 2->0 is indistinguishable from 2->5, given only the angle of the swipe)
A DFS search with pruning to remove solutions with unprintable characters recovers the correct PIN code in ~10 seconds.
