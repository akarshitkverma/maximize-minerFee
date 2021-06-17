# maximize-minerFee

An optimized way to maximize Miner Fee while creating Blocks.

## Problem Statement

- To create a valid block from the pending transactions, maximizing the fee to the miner.

### Input

- `mempool.csv` file, with the format: `<txid>,<fee>,<weight>,<parent_txids>`

### Output

- The output from the program is `block.txt` with txids, separated by newlines, which make a valid block.

### Constraints

- Block Weight = 4,000,000
- For a valid block, parent transactions should appear before their children in the output.

## Approach

- The problem looked like a Knapsack Problem in the first look, which can be solved using Greedy Approach. However, looking more closely, we understand that there are dependencies(parents) involved. To handle this, we have created equivalent transactions by cumulating their weights and fees.

### Steps:

- If a transaction is not a parent, calculate an equivalent independent transaction by cumulating it with its parent(adding up weight and fee). We are not doing this for any parent transaction as they will be covered while making their children's equivalents. We have used a recursive DFS for this purpose.
- We now sort our list of independent transactions by feerate(fee/weight) in descending order.
- Then we select the most profitable transaction from the independent transaction, such that we stick to the constraint.
- Lastly, we put those transactions in the block(ensuring that all their parents are already placed be). For this, also we make use of recursive DFS.

It is an overview. Check out the main.py file to understand more how the code works.

## Results

- **Block Weight: 3999808**
- **Block Fee: 5797979**

## References

- [Miner Fees Article by Bitcoin Wiki](https://en.bitcoin.it/wiki/Miner_fees#Technical_info)
