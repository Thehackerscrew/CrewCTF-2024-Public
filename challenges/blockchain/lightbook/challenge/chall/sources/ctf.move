/// Module: stable_coin
module challenge::ctf {
    // ---------------------------------------------------
    // DEPENDENCIES
    // ---------------------------------------------------

    use sui::object::{Self, UID};
    use sui::balance::{Self, Balance, Supply};
    use sui::coin::{Self, Coin};
    use sui::sui::{SUI};
    use sui::transfer::{Self};
    use sui::clock::{Self, Clock};
    use sui::tx_context::{Self, TxContext};
    
    use deepbook::clob_v2::{Self, Pool};
    use deepbook::custodian_v2::{Self, AccountCap};

    use challenge::hcoin::{Self, HCOIN};
    use challenge::cusd::{Self, CUSD};


    // ---------------------------------------------------
    // STRUCTS
    // ---------------------------------------------------

    struct Storage has key, store {
        id: UID,
        pool: clob_v2::Pool<HCOIN, CUSD>,
        airdrop_base: Coin<HCOIN>,
        airdrop_quote: Coin<CUSD>,
        is_solved: bool,
    }


    // ---------------------------------------------------
    // CONSTANTS
    // ---------------------------------------------------

    const ZERO: u64 = 0;
    const TICK_SIZE: u64 = 10_000_000;
    const LOT_SIZE: u64 = 10_000_000;
    const DECIMALS: u64  = 1_000_000_000;
    const ONE: u64 = 1_000_000_000;
    const TWO: u64 = 2_000_000_000;
    const BID: bool = true;
    const U64_MAX: u64 = 18446744073709551615;

    const NO_RESTRICTION: u8 = 0;
    const IMMEDIATE_OR_CANCEL: u8 = 1;


    // ---------------------------------------------------
    // FUNCTIONS
    // ---------------------------------------------------

    #[test_only]
    public fun construct_ctf_scenairo(
        fee: Coin<SUI>,
        hcoin_cap: &mut coin::TreasuryCap<HCOIN>,
        cusd_cap: &mut coin::TreasuryCap<CUSD>,
        clock: &Clock,
        ctx: &mut TxContext,
    ): Storage {
        let pool: Pool<HCOIN, CUSD> = clob_v2::create_customized_pool_with_return<HCOIN, CUSD>(
            TICK_SIZE,
            LOT_SIZE,
            ZERO,
            ZERO,
            fee,
            ctx,
        );

        let airdrop_base = coin::mint(hcoin_cap, 300 * DECIMALS, ctx);
        let airdrop_quote = coin::mint(cusd_cap, 600 * DECIMALS, ctx);

        let storage = Storage {
            id: object::new(ctx),
            pool,
            airdrop_base,
            airdrop_quote,
            is_solved: false,
        };

        let tick_amt = 100 * DECIMALS;
        let diff = TICK_SIZE;
        let limit = 6;

        let minted_hcoin = coin::mint(hcoin_cap, 10000 * DECIMALS, ctx);
        let minted_cusd = coin::mint(cusd_cap, 10000 * DECIMALS, ctx);

        let pool = get_mut_pool(&mut storage);
        let account_cap: AccountCap = clob_v2::create_account(ctx);

        clob_v2::deposit_base(pool, minted_hcoin, &account_cap);
        clob_v2::deposit_quote(pool, minted_cusd, &account_cap);

        let i = 1;

        while (i <= limit) {
            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                TWO - diff * i,
                tick_amt,
                0,
                BID,
                U64_MAX,
                NO_RESTRICTION,
                clock,
                &account_cap,
                ctx,
            );

            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                TWO + diff * i,
                tick_amt,
                0,
                !BID,
                U64_MAX,
                NO_RESTRICTION,
                clock,
                &account_cap,
                ctx,
            );

            i = i + 1;
        };

        transfer::public_transfer(account_cap, tx_context::sender(ctx));
        storage
    }

    public fun get_airdrop_base(ctf_storage: &mut Storage, amount: u64, ctx: &mut TxContext): Coin<HCOIN> {
        coin::split(&mut ctf_storage.airdrop_base, amount, ctx)
    }

    public fun get_airdrop_quote(ctf_storage: &mut Storage, amount: u64, ctx: &mut TxContext): Coin<CUSD> {
        coin::split(&mut ctf_storage.airdrop_quote, amount, ctx)
    }

    public fun get_pool(ctf_storage: &Storage): &Pool<HCOIN, CUSD> {
        &ctf_storage.pool
    }

    public fun get_mut_pool(ctf_storage: &mut Storage): &mut Pool<HCOIN, CUSD> {
        &mut ctf_storage.pool
    }

    public fun solve(ctf_storage: &mut Storage, my_cusd: &Coin<CUSD>) {
        if(coin::value(my_cusd) >= 2500 * DECIMALS) ctf_storage.is_solved = true;
    }

    public fun is_solved(ctf_storage: &Storage) {
        assert!(ctf_storage.is_solved, 0);
    }

}
