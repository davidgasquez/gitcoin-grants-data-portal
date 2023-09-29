with source as (
    select * from {{ source('public', 'raw_round_votes') }}
),

renamed as (
    select
        chainId as chain_id,
        roundId as round_id,
        id,
        transaction,
        blockNumber as block_number,
        projectId as project_id,
        applicationId as application_id,
        voter,
        grantAddress as grant_address,
        token,
        amount,
        amountUSD as amount_usd,
        amountRoundToken as amount_round_token
    from source
)

select * from renamed