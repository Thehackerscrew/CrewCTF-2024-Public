module challenge::solve {
    use sui::{balance, clock, coin, object, transfer, tx_context};
    use deepbook::{clob_v2, custodian_v2, math, critbit, order_query};

    use challenge::hcoin::HCOIN;
    use challenge::cusd::CUSD; 
    use challenge::ctf;
    use challenge::otter_strategy;
    
    public fun solve(
        storage: &mut ctf::Storage, 
        vault: &mut otter_strategy::Vault,
        clock: &clock::Clock,
        ctx: &mut tx_context::TxContext,
    ) {
        //// your code



    }
}
