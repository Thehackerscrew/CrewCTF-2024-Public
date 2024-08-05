module challenge::cusd {
    use sui::transfer::{Self};
    use sui::coin::{Self, TreasuryCap};
    use sui::tx_context::{Self, TxContext};
    use std::option;

    struct CUSD has drop {}

    fun init(witness: CUSD, ctx: &mut TxContext) {
        let (treasury_cap, coinMetadata) = coin::create_currency<CUSD>(witness, 9, b"CUSD", b"CUSD" , b"crew usd", option::none(), ctx);
        transfer::public_transfer(treasury_cap, tx_context::sender(ctx));
        transfer::public_freeze_object(coinMetadata);
    }

    #[test_only]
    public fun init_test(ctx: &mut TxContext): TreasuryCap<CUSD> {
        let witness = CUSD{};
        let (treasury_cap, coinMetadata) = coin::create_currency<CUSD>(witness, 9, b"CUSD", b"CUSD" , b"crew usd", option::none(), ctx);
        transfer::public_freeze_object(coinMetadata);
        treasury_cap
    }
}
