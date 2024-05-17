select
    min(auction_id) as start_auction,
    max(auction_id) as end_auction
from
    settlement_scores
where
    block_deadline >= {{start_block}} 
        and
    block_deadline <= {{end_block}}