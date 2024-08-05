This is a 1-day challenge of deepbook-v2 based on https://github.com/MystenLabs/sui/commit/f2651e9bb0e40cdf24b2d0656a76f3f60f7847d2

 

## Root Cause
Deepbook uses an on-chain orderbook and employs a critbit tree to sort numerous orders.

When you send a query to the tree, it finds the key closest to the one you're searching for using critbit::find_closest_key.

 

If the tree contains the keys 10, 13, and 15, the key closest to 13 is, naturally, 13.

However, if the tree only contains 10 and 15, what would be the key closest to 13?

 

This question can extend to clob_v2::get_level2_book_status_{bid, ask}_side.

 

When we want to query orders between 10 and 15, but the tree lacks entries at 10 and 15, the query will find the closest keys. Let's call these low_closest_key and high_closest_key. For accurate results, the condition 10 <= low_closest_key <= high_closest_key <= 15 must be satisfied. 

However, since the code doesn't guarantee this condition, the sparser tree, the greater the discrepancy between actual values and the query results could be.

 

 

## Solve
 

bid_book: [1.94, 1.99]

ask_book: [2.01, 2.06]

 

1. set the ask_price to 2.06 and the bid_price to 2.05

2. run otter_strategy::execute

3. the key closest to 2.00 is 1.99, and the closest one to 2.05 is 2.05, orders of $1.99 would be removed. 

4. set the bid_price to 2.05 again and repeat step 2, the closest key to 2.00 becomes 1.98.

Repeating this process will eventually empty the bid_book.

 

5. set the bid_price to 2.05 and place a bid around 1.88. this makes the closest key to 2.00 become 1.88, causing the otter_strategy to place an ask at 1.88, allowing you to buy at a lower price.

6. sell it back at a higher price using the otter_strategy and repeat steps 5 and 6 for profit.

 

 

fun fact) setting the bid_price to 1.94 and the ask_price to 1.95 will be failed due to the structure of the critbit tree.