## UNDER CONSTRUCTION

This repository contains a script that uses the Cow Protocol API as well as the Gnosis Scan API to compute solver rewards of the solver competition of CoW Protocol on Gnosis Chain.

The script is not yet automated, and requires access to the orderbook db. The flow is the following:

1. Execute the compute_block_range.py script, passing 3 integer command-line parameters corresponding to year, month, day of the starting day of the accounting. E.g., execute

`python3.11 compute_block_range.py 2024 4 9`

in order to get the first block after April 9th, 2024, 00:00 UTC and the last block before April 16th, 2024, 00:00 UTC. Note the block range always spans 7 days.

2. Run the get_auction_range sql query with the above computed start and end block in the prod and barn databased in order to get the first and last auction that need to be considered in the payout script for each environment.

3. Execute the payout_script with the above auction ids in order to generate a csv with the solver payouts. E.g.,

`python3.11 payout_script.py 10055506 10055700 21179761 21179900`

### Rewards schema

7500 xDAI have been allocated per week for solver rewards, with the following distribution:
- 20% for the price estimation competition; this corresponds that 1,500 XDAI per week
- 30% for performance rewars for the solver competition; this corresponds to 2,250 XDAI per week. To compute these, we use the second-price auction mechanism described in CIP-38, with adjusted upper and lower caps.
- 50% for consistency for the solver competition; this corresponds to 3,750 xDAI per week. Moreover, the best 3 solutions in each auction are rewarded 20% more than the rest. What this means is that for each auction, all valid solutions except for the best 3 receive 1 participation token, while the best three receive 1.2 participation tokens each. We then compute the total number of participation tokens given out, and we distribute the 3,750 xDAI proportional to the number of participation tokens each solver has received.

Price estimation 
