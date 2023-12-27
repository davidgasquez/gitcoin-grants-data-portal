with source as (
    select * from {{ source('public', 'raw_rounds') }}
),

renamed as (
    select
        lower(id) as id,
        amountUSD as amount_usd,
        votes,
        lower(token) as token,
        matchAmount as match_amount,
        matchAmountUSD as match_amount_usd,
        uniqueContributors as unique_contributors,
        applicationMetaPtr as application_meta_ptr,
        applicationMetadata as application_metadata,
        metaPtr as meta_ptr,
        metadata as metadata,
        applicationsStartTime as applications_start_time,
        applicationsEndTime as applications_end_time,
        roundStartTime as round_start_time,
        roundEndTime as round_end_time,
        createdAtBlock as created_at_block,
        updatedAtBlock as updated_at_block,
        chainId as chain_id
    from source
),

extracted_metadata as (
    select
        *,
        json_extract_path_text(metadata, 'name') as name,
        json_extract_path_text(metadata, 'roundType') as round_type,
        lower(json_extract_path_text(metadata, 'programContractAddress')) as program_address,
        json_extract_path_text(metadata, '$.quadraticFundingConfig.sybilDefense')::boolean as sybil_defense
    from renamed
)

select * from extracted_metadata
