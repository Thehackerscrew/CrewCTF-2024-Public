# Tree V2

This challenge is based on the seconde preimage attack on Merkle tree. For more information, please refer to the following article:

[https://www.rareskills.io/post/merkle-tree-second-preimage-attack](https://www.rareskills.io/post/merkle-tree-second-preimage-attack)


This repo includes:
- `challenge`: the challenge server based on https://github.com/minaminao/tokyo-payload
- `solution`: the author's solver

## Description

## Generate the distributed files

```
make generate-distfiles
```

## Launch a challenge server

```
make start-challenge-server
```

## Access the challenge server

```
nc localhost 31337
```

Good luck!

## Solve script

```
forge script solver/script/Solve.s.sol --rpc-url <rpc_url> --private-key <private_key> --broadcast
```