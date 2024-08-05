/// Module: stable_coin
module challenge::poc {
    //// for you
    use challenge::solve;

    use challenge::hcoin::{Self};
    use challenge::cusd::{Self};
    use challenge::ctf::{Self};
    use challenge::otter_strategy::{Self};
    
    use sui::tx_context;
    use sui::clock;
    use sui::sui::{SUI};
    use sui::coin;
    use sui::transfer;

    const ADMIN: address = @0x1234;
    const USER: address = @0x5678;

    #[test]
    fun poc() {
        //// setup
        let admin = tx_context::new_from_hint(ADMIN, 0, 0, 0, 0);
        let user = tx_context::new_from_hint(USER, 0, 0, 0, 0);

        let hcoin_tc = hcoin::init_test(&mut admin);
        let cusd_tc = cusd::init_test(&mut admin);

        let clock = clock::create_for_testing(&mut admin);

        let storage = ctf::construct_ctf_scenairo(
            coin::mint_for_testing<SUI>(100 * 1_000_000_000, &mut admin),
            &mut hcoin_tc,
            &mut cusd_tc,
            &clock,
            &mut admin,
        );

        let vault = otter_strategy::create_vault(
            &mut hcoin_tc,
            &mut cusd_tc,
            &mut admin,
        );

        //// your code
        solve::solve(
            &mut storage,
            &mut vault,
            &clock,
            &mut user,
        );

        //// verify
        ctf::is_solved(&storage);

        //// clean
        clock::destroy_for_testing(clock);
        transfer::public_transfer(storage, tx_context::sender(&admin));
        transfer::public_transfer(vault, tx_context::sender(&admin));
        transfer::public_transfer(hcoin_tc, tx_context::sender(&admin));
        transfer::public_transfer(cusd_tc, tx_context::sender(&admin));
    }


}
