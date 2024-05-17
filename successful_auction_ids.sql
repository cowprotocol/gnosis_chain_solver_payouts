select
    s.auction_id
from
    settlements s join settlement_scores ss on s.auction_id=ss.auction_id
    where ss.block_deadline >= {{start_block}} AND ss.block_deadline <= {{end_block}}