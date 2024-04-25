select
    json->'solutions' as competition_info
from solver_competitions
where id in {{auction_list}}