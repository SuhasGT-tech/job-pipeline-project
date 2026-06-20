select
    date_trunc('day', first_seen) as day,
    count(*) as new_postings
from {{ ref('stg_jobs') }}
group by 1
order by 1
