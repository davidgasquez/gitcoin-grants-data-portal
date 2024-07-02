-- disabled due to https://github.com/davidgasquez/gitcoin-grants-data-portal/issues/88
{{ config(
    enabled=false
)}}

with source as (
    select * from {{ source('public', 'raw_hypercert_claims') }}
),

renamed as (
    select
        --id,
        tokenID as token_id,
        lower(contract) as contract,
        uri as ipfs_cid,
        try_cast(totalUnits as bigint) as total_units,
        lower(creator) as creator
    from source
)

select * from renamed
