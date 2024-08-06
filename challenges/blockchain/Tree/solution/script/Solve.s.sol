// SPDX-License-Identifier: MIT

pragma solidity 0.8.25;

import "forge-std/Script.sol";

import "../src/Challenge.sol";

contract Solve is Script {

    Challenge challenge = Challenge(0xd832b1016fd2a99721732A18ccca0421Dd1FeDb0);

    function run() public {
        vm.startBroadcast();
        /***
         *     __       __                      __        __         ________                                   
         *    |  \     /  \                    |  \      |  \       |        \                                  
         *    | $$\   /  $$  ______    ______  | $$   __ | $$  ______\$$$$$$$$______    ______    ______        
         *    | $$$\ /  $$$ /      \  /      \ | $$  /  \| $$ /      \ | $$  /      \  /      \  /      \       
         *    | $$$$\  $$$$|  $$$$$$\|  $$$$$$\| $$_/  $$| $$|  $$$$$$\| $$ |  $$$$$$\|  $$$$$$\|  $$$$$$\      
         *    | $$\$$ $$ $$| $$    $$| $$   \$$| $$   $$ | $$| $$    $$| $$ | $$   \$$| $$    $$| $$    $$      
         *    | $$ \$$$| $$| $$$$$$$$| $$      | $$$$$$\ | $$| $$$$$$$$| $$ | $$      | $$$$$$$$| $$$$$$$$      
         *    | $$  \$ | $$ \$$     \| $$      | $$  \$$\| $$ \$$     \| $$ | $$       \$$     \ \$$     \      
         *     \$$      \$$  \$$$$$$$ \$$       \$$   \$$ \$$  \$$$$$$$ \$$  \$$        \$$$$$$$  \$$$$$$$      
         *                                                                                                      
         *                                                                                                      
         *                                                                                                      
         */
        bytes20 pHash = hex"efabb566b9a30d074684005482d0ef08f4a76b4b";

        bytes20 vHash = hex"5c1562f32e1d9c715d41b10dde0eb3088353a980";
        bytes11 epoch = bytes11(vHash);
        uint72 amount = uint72(uint256(uint160(vHash)));


        bytes20[] memory proofs = new bytes20[](3);
        proofs[0] = bytes20(hex"81ef08937a2c85f8ef6bc79ce82d0c9c7d10a119");
        proofs[1] = bytes20(hex"1852fe43fe3f29f9880af8c4adda245f3959cd5d");
        proofs[2] = bytes20(hex"a672fa083f7d075135f8de011d2597f3e5177371");

        challenge.merkleAirdrop().claim(epoch, amount,address(pHash), proofs);

        challenge.merkleAirdrop().removeDust();

        require(challenge.isSolved(), "Challenge not solved");


        // for the memory, never forget (this was supposedto be the second part of the challenge, but it was removed from the final version cause of SKILL ISSUE and time)
        /***
        *     ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓██████████████▓▒░░▒▓████████▓▒░      
        *    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             
        *    ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             
        *    ░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░        
        *    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             
        *    ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             
        *     ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░      
        *                                                                      
        *                                                                      
        */    

        vm.stopBroadcast();
    }
}