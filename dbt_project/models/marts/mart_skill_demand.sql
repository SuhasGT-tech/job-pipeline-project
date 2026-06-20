with staged as (

    select * from {{ ref('stg_jobs') }}

),

unpivoted as (

    select 'sql' as skill, has_sql as mentioned, created from staged
    union all
    select 'python', has_python, created from staged
    union all
    select 'power_bi', has_power_bi, created from staged
    union all
    select 'excel', has_excel, created from staged
    union all
    select 'snowflake', has_snowflake, created from staged
    union all
    select 'airflow', has_airflow, created from staged
    union all
    select 'dbt', has_dbt, created from staged
    union all
    select 'spark', has_spark, created from staged
    union all
    select 'aws', has_aws, created from staged
    union all
    select 'azure', has_azure, created from staged
    union all
    select 'gcp', has_gcp, created from staged
    union all
    select 'tableau', has_tableau, created from staged
    union all
    select 'sap_stack', has_sap, created from staged

)

select
    skill,
    date_trunc('week', created) as week,
    count(*) filter (where mentioned) as postings_mentioning
from unpivoted
group by 1, 2
order by 2 desc, 3 desc
