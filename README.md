## UNDER CONSTRUCTION

This repository contains a script that uses the Cow Protocol API as well as the Gnosis Scan API to compute solver rewards of the solver competition of CoW Protocol on Gnosis Chain.

The script is not yet automated, and requires access to the orderbook db. The flow is the following:

1. Execute the compute_block_range.py script, passing 3 command-line parameters as year, month, day. E.g.,

`python3.11 compute_block_range.py 2024 4 9`

in order to get the first block after April 9th, 2024, 00:00 UTC and the last block before April 17th, 2024, 00:00 UTC. Note the block range always spans 7 days.

2. Run the get_auction_range sql query with the above computed start and end block in the prod and barn databased in order to get the first and last auction that need to be considered in the payout script.

3. Execute the payout_script with the above auction ids in order to generate a csv with the solver payouts. E.g.,

`python3.11 payout_script.py 10055506 10055700 21179761 21179900`
