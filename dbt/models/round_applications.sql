with source as (
    select * from {{ source('public', 'raw_round_applications') }}
),

renamed as (
    select
        lower(chainId) as chain_id,
        lower(roundId) as round_id,
        id,
        projectId as project_id,
        status,
        amountUSD as amount_usd,
        votes,
        uniqueContributors as unique_contributors,
        metadata,
        createdAtBlock as created_at_block,
        statusUpdatedAtBlock as status_updated_at_block,
        statusSnapshots as status_snapshots
    from source
),

extracted_metadata as (
    select
        *,
        json_extract_path_text(metadata, 'signature') as signature,
        lower(json_extract_path_text(metadata, '$.application.recipient')) as recipient
    from renamed
)

select * from extracted_metadata
