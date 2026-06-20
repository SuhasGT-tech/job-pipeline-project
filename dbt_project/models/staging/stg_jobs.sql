with source as (

    select * from {{ source('raw', 'jobs_raw') }}

),

cleaned as (

    select
        id,
        trim(title) as title,
        company,
        location,
        description,
        salary_min,
        salary_max,
        contract_type,
        category,
        created,
        first_seen,
        last_seen,
        lower(coalesce(description, '') || ' ' || coalesce(title, '')) as searchable_text
    from source
    where title is not null

)

select
    id,
    title,
    company,
    location,
    description,
    salary_min,
    salary_max,
    contract_type,
    category,
    created,
    first_seen,
    last_seen,
    searchable_text ilike '%sql%' as has_sql,
    searchable_text ilike '%python%' as has_python,
    (searchable_text ilike '%power bi%' or searchable_text ilike '%powerbi%') as has_power_bi,
    searchable_text ilike '%excel%' as has_excel,
    searchable_text ilike '%snowflake%' as has_snowflake,
    searchable_text ilike '%airflow%' as has_airflow,
    searchable_text ilike '%dbt%' as has_dbt,
    (searchable_text ilike '%spark%' or searchable_text ilike '%pyspark%') as has_spark,
    searchable_text ilike '%aws%' as has_aws,
    searchable_text ilike '%azure%' as has_azure,
    (searchable_text ilike '%gcp%' or searchable_text ilike '%google cloud%') as has_gcp,
    searchable_text ilike '%tableau%' as has_tableau,
    (searchable_text ilike '%sap%' or searchable_text ilike '%bods%' or searchable_text ilike '%businessobjects%') as has_sap
from cleaned
