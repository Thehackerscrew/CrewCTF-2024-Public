module challenge::hcoin {
    use sui::transfer::{Self};
    use sui::coin::{Self, TreasuryCap};
    use sui::tx_context::{Self, TxContext};
    use std::option;

    struct HCOIN has drop {}

    fun init(witness: HCOIN, ctx: &mut TxContext) {
        let (treasury_cap, coinMetadata) = coin::create_currency<HCOIN>(witness, 9, b"HCOIN", b"HCOIN" , b"hackers coin", option::none(), ctx);
        transfer::public_transfer(treasury_cap, tx_context::sender(ctx));
        transfer::public_freeze_object(coinMetadata);
    }

    #[test_only]
    public fun init_test(ctx: &mut TxContext): TreasuryCap<HCOIN> {
        let witness = HCOIN{};
        let (treasury_cap, coinMetadata) = coin::create_currency<HCOIN>(witness, 9, b"HCOIN", b"HCOIN" , b"hackers coin", option::none(), ctx);
        transfer::public_freeze_object(coinMetadata);
        treasury_cap
    }
}
