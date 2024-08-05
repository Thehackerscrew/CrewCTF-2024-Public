# DEBUGjail

Many different leaks are available, the provided script utilizes an IO port which belongs to the IBM 8514 graphics card (or any compatible card).
It will happily print any 16-bit value written to this port to stdout which is very convenient.
Pretty much any two operations which print anything to stdout could be used to leak the secret bit by bit.

`config -securemode` should prevent a trivial bypass where the challenge directory could be mounted in dosbox.
