with source as (
    select * from {{ source('public', 'raw_karmahq_attestations') }}
),

renamed as (
    select
        lower(attester) as attester,
        lower(recipient) as recipient,
        isOffchain as is_offchain,
        decodedDataJson as json,
        JSON_EXTRACT(decodedDataJson->>'$[0].value.value', '$.hash') as ipfs_cid,
        JSON_EXTRACT(decodedDataJson->>'$[0].value.value', '$.title') as title
    from source
)

select * from renamed
