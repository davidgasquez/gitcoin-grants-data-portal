with source as (
    select * from {{ source('public', 'raw_hypercert_claims') }}
),

renamed as (
    select
        id,
        tokenID as token_id,
        lower(contract) as contract,
        uri as ipfs_cid,
        CAST(totalUnits AS BIGINT) as total_units,
        lower(creator) as creator
    from source
)

select * from renamed
