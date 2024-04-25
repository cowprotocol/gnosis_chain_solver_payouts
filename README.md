## UNDER CONSTRUCTION

This repository contains a script that uses the Cow Protocol API as well as the Gnosis Scan API to compute solver rewards of the solver competition of CoW Protocol on Gnosis Chain.

### Rewards schema

7500 xDAI have been allocated per week for solver rewards, with the following distribution:
- 20% for the price estimation competition; this corresponds that 1,500 XDAI per week
- 30% for performance rewars for the solver competition; this corresponds to 2,250 XDAI per week. To compute these, we use the second-price auction mechanism described in CIP-38, with adjusted upper and lower caps.
- 50% for consistency for the solver competition; this corresponds to 3,750 xDAI per week. Moreover, the best 3 solutions in each auction are rewarded 20% more than the rest. What this means is that for each auction, all valid solutions except for the best 3 receive 1 participation token each, while the best three receive 1.2 participation tokens each. We then compute the total number of participation tokens given out, and we distribute the 3,750 xDAI proportional to the number of participation tokens each solver has received.

The rewards mechanism follows CIP-38, with the following caps being currently chosen: 25 xDAI as an upper cap for performance and -5 xDAI as a lower cap for penalties. Rewards for each class (performance, consistency, quoting) are then rescaled to match the budget.

### Usage

The script requires access to the orderbook db. One needs to execute the following:

`python3.11 main_script.py 2024 4 9`

and a csv file in the `/out` folder is generated with the transfers.

