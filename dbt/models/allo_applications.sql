with source as (
    select * from {{ source('public', 'raw_allo_applications') }}
),

renamed as (
    select
        anchorAddress as anchor_address,
        chainId as chain_id,
        createdAtBlock as created_at_block,
        createdByAddress as created_by_address,
        lower(id) as id,
        metadata,
        metadata->>'$.signature' as metadata_signature,
        lower(metadata->>'$.application.recipient') as metadata_application_recipient,
        metadataCid as metadata_cid,
        nodeId as node_id,
        lower(projectId) as project_id,
        lower(roundId) as round_id,
        status,
        statusSnapshots as status_snapshots,
        statusUpdatedAtBlock as status_updated_at_block,
        tags,
        totalAmountDonatedInUsd as total_amount_donated_in_usd,
        totalDonationsCount as total_donations_count,
        uniqueDonorsCount as unique_donors_count
    from source
)

select * from renamed
