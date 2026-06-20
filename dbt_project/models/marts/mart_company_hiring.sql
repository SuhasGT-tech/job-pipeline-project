select
    company,
    count(*) as open_postings,
    min(first_seen) as first_seen,
    max(last_seen) as last_seen
from {{ ref('stg_jobs') }}
where company is not null
group by 1
order by 2 desc
