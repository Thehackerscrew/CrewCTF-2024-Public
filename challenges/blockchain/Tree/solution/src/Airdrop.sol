// SPDX-License-Identifier: AGPL-3.0-only
pragma solidity 0.8.25;

import "./Token.sol";


contract MerkleAirdrop {
/***
 *          .o.        o8o           oooooooooo.                                 
 *         .888.       `"'           `888'   `Y8b                                
 *        .8"888.     oooo  oooo d8b  888      888 oooo d8b  .ooooo.  oo.ooooo.  
 *       .8' `888.    `888  `888""8P  888      888 `888""8P d88' `88b  888' `88b 
 *      .88ooo8888.    888   888      888      888  888     888   888  888   888 
 *     .8'     `888.   888   888      888     d88'  888     888   888  888   888 
 *    o88o     o8888o o888o d888b    o888bood8P'   d888b    `Y8bod8P'  888bod8P' 
 *                                                                     888       
 *                                                                    o888o      
 *                                                                               
 */

  // (☞ﾟヮﾟ)☞ Constants 
  bytes20 public immutable merkleRoot;

  // (☞ﾟヮﾟ)☞ Variables
  Token public token;
  mapping(address => bool) public hasClaimed;
  uint256 treshold;

  // (╯°□°)╯︵ ɹoɹɹƎ
  error AlreadyClaimed();
  error NotInMerkle();

  // (☞ﾟヮﾟ)☞ Events  
  event Claim(address indexed to, uint256 amount);
  event DustClaimed(address indexed to, uint256 amount);


  constructor(bytes20 _merkleRoot, address _tokenAddress, uint256 _treshold) { 
    merkleRoot = _merkleRoot;
    token = Token(_tokenAddress); 
    treshold = _treshold;
  }

  function claim(bytes11 epoch, uint72 amount, address to, bytes20[] calldata proof) external {
    if (hasClaimed[to]) revert AlreadyClaimed();

    bytes20 leaf = ripemd160(bytes.concat(ripemd160(abi.encodePacked(epoch, amount, to))));

    bool isValidLeaf = verify(leaf, merkleRoot, proof);
    if (!isValidLeaf) revert NotInMerkle();

    hasClaimed[to] = true;
    token.transfer(to, amount);
    emit Claim(to, amount);
  }

  
  function removeDust() external {
    uint256 balance = token.balanceOf(address(this));
    if (balance <= treshold) {
      token.transfer(msg.sender, balance);
      emit DustClaimed(msg.sender, balance);
    }
  }



/***
 *    ooo        ooooo                    oooo        oooo            ooooooooo.                                 .o88o. 
 *    `88.       .888'                    `888        `888            `888   `Y88.                               888 `" 
 *     888b     d'888   .ooooo.  oooo d8b  888  oooo   888   .ooooo.   888   .d88' oooo d8b  .ooooo.   .ooooo.  o888oo  
 *     8 Y88. .P  888  d88' `88b `888""8P  888 .8P'    888  d88' `88b  888ooo88P'  `888""8P d88' `88b d88' `88b  888    
 *     8  `888'   888  888ooo888  888      888888.     888  888ooo888  888          888     888   888 888   888  888    
 *     8    Y     888  888    .o  888      888 `88b.   888  888    .o  888          888     888   888 888   888  888    
 *    o8o        o888o `Y8bod8P' d888b    o888o o888o o888o `Y8bod8P' o888o        d888b    `Y8bod8P' `Y8bod8P' o888o   
 * 
 *                                                                                                                                                                                                                                        
 */       
  function verify(
    bytes20 leaf,
    bytes20 root,
    bytes20[] memory proof
  ) public pure returns (bool) {
      bytes20 currentHash = leaf;
      for (uint256 i; i < proof.length; i++) {
          currentHash = _hash(currentHash, proof[i]);
      }
      return currentHash == root;
  }

  function _hash(bytes20 a, bytes20 b) private pure returns (bytes20) {
    return
      a < b
          ? ripemd160(bytes.concat(ripemd160(abi.encodePacked(a, b))))
          : ripemd160(bytes.concat(ripemd160(abi.encodePacked(b, a))));
  }
}