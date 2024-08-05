/// Module: stable_coin
module challenge::otter_strategy {
    // ---------------------------------------------------
    // DEPENDENCIES
    // ---------------------------------------------------
    use sui::object::{Self, UID};
    use sui::coin::{Self, Coin};
    use sui::clock::{Clock};
    use sui::tx_context::{TxContext};

    use std::option;
    use std::vector;
    
    use deepbook::clob_v2::{Self, Pool};
    use deepbook::custodian_v2::{AccountCap};

    use challenge::hcoin::{HCOIN};
    use challenge::cusd::{CUSD};


    // ---------------------------------------------------
    // STRUCTS
    // ---------------------------------------------------

    struct Vault has key, store {
        id: UID,
        account_cap: AccountCap,
        hcoin: Coin<HCOIN>,
        cusd: Coin<CUSD>,
    }


    // ---------------------------------------------------
    // CONSTANTS
    // ---------------------------------------------------

    const DECIMALS: u64 = 1_000_000_000;

    const BUY_THRESHOLD: u64 = 1_950_000_000;
    const LIMIT: u64 = 2_000_000_000;
    const SELL_THRESHOLD: u64 = 2_050_000_000;

    const BID: bool = true;

    // ---------------------------------------------------
    // FUNCTIONS
    // ---------------------------------------------------

    public fun create_vault(
        hcoin_cap: &mut coin::TreasuryCap<HCOIN>,
        cusd_cap: &mut coin::TreasuryCap<CUSD>,
        ctx: &mut TxContext, 
    ): Vault {
        let vault = Vault {
            id: object::new(ctx),
            account_cap: clob_v2::create_account(ctx),
            hcoin: coin::mint(hcoin_cap, 20000 * DECIMALS, ctx),
            cusd: coin::mint(cusd_cap, 20000 * DECIMALS, ctx),
        };

        vault
    }

    // simple is the best:
    public fun execute(
        pool: &mut Pool<HCOIN, CUSD>, 
        vault: &mut Vault,
        is_bid: bool,
        clock: &Clock,
        ctx: &mut TxContext, 
    ) {
        let account_cap = &vault.account_cap;

        let (bid_price, ask_price) = clob_v2::get_market_price<HCOIN, CUSD>(
            pool,
        );

        if (option::is_some(&ask_price) && is_bid) {
            let ask_price = option::destroy_some(ask_price);
            if (ask_price > BUY_THRESHOLD) return;

            let (prices, depths) = clob_v2::get_level2_book_status_ask_side<HCOIN, CUSD>(
                pool,
                BUY_THRESHOLD,
                LIMIT,
                clock,
            );

            let total_required_base_amount = 0;
            let total_required_quote_amount = 0;

            let len = vector::length(&prices);
            let i = 0;

            while(i < len) {
                let mul_amt = (*vector::borrow(&prices, i) as u128) * (*vector::borrow(&depths, i) as u128) / (DECIMALS as u128);
                total_required_base_amount = total_required_base_amount + *vector::borrow(&depths, i);
                total_required_quote_amount = total_required_quote_amount + (mul_amt as u64);
                i = i + 1;
            };

            if(coin::value(&vault.cusd) < total_required_quote_amount) return;
            if(total_required_base_amount == 0) return;

            let amount_hcoin = coin::value(&vault.hcoin);
            let amount_cusd = coin::value(&vault.cusd);
            let (remaining_hcoin, remaining_cusd) = clob_v2::place_market_order(
                pool,
                account_cap,
                0,
                total_required_base_amount,
                BID,
                coin::split(&mut vault.hcoin, amount_hcoin, ctx),
                coin::split(&mut vault.cusd, amount_cusd, ctx),
                clock,
                ctx,
            );
            coin::join(&mut vault.hcoin, remaining_hcoin);
            coin::join(&mut vault.cusd, remaining_cusd);
        };


        if (option::is_some(&bid_price) && !is_bid) {
            let bid_price = option::destroy_some(bid_price);
            if (bid_price < SELL_THRESHOLD) return;

            let (prices, depths) = clob_v2::get_level2_book_status_bid_side<HCOIN, CUSD>(
                pool,
                LIMIT,
                SELL_THRESHOLD, 
                clock,
            );

            let total_required_base_amount = 0;
            let total_required_quote_amount = 0;

            let len = vector::length(&prices);
            let i = 0;

            while(i < len) {
                let mul_amt = (*vector::borrow(&prices, i) as u128) * (*vector::borrow(&depths, i) as u128) / (DECIMALS as u128);
                total_required_base_amount = total_required_base_amount + *vector::borrow(&depths, i);
                total_required_quote_amount = total_required_quote_amount + (mul_amt as u64);
                i = i + 1;
            };

            if(coin::value(&vault.hcoin) < total_required_base_amount) return;
            if(total_required_base_amount == 0) return;
            let amount_hcoin = coin::value(&vault.hcoin);
            let amount_cusd = coin::value(&vault.cusd);
            let (remaining_hcoin, remaining_cusd) = clob_v2::place_market_order(
                pool,
                account_cap,
                0,
                total_required_base_amount,
                !BID,
                coin::split(&mut vault.hcoin, amount_hcoin, ctx),
                coin::split(&mut vault.cusd, amount_cusd, ctx),
                clock,
                ctx,
            );
            coin::join(&mut vault.hcoin, remaining_hcoin);
            coin::join(&mut vault.cusd, remaining_cusd);
        };
    }

}
