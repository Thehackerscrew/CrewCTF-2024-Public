// SPDX-License-Identifier: MIT

pragma solidity 0.8.26;

import "./Token.sol";
import "./Airdrop.sol";


contract Challenge {

    Token public token;
    MerkleAirdrop public merkleAirdrop;

    uint256 valueAirdrop = 300 * 10 ** 18;
    uint256 tresHold = 50 * 10 ** 18;

    address constant public PLAYER = 0xCaffE305b3Cc9A39028393D3F338f2a70966Cb85;

    constructor() payable {
        token = new Token("crewToken", "CT", 1000);
        merkleAirdrop = new MerkleAirdrop(hex"666370627f747110074a729f34cae2509ac3df8c", address(token), tresHold);

        token.transfer(address(merkleAirdrop), valueAirdrop);
    }

    function isSolved() public view returns(bool) {
        return token.balanceOf(address(merkleAirdrop)) == 0;
    }
}