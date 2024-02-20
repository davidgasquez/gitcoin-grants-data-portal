with source as (
    select * from {{ source('public', 'raw_allo_prices') }}
),

renamed as (
    select
        blockNumber as block_number,
        lower(chainId) as chain_id,
        id,
        nodeId as node_id,
        priceInUsd as price_in_usd,
        timestamp,
        lower(tokenAddress) as token_address,
    from source
)

select * from renamed
