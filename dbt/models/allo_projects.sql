with source as (
      select * from {{ source('public', 'raw_allo_projects') }}
),

renamed as (
    select
        anchorAddress as anchor_address,
        chainId as chain_id,
        createdAtBlock as created_at_block,
        lower(createdByAddress) as created_by_address,
        id,
        metadata as metadata,
        metadata->>'title' as title,
        metadata->>'description' as description,
        metadata->>'website' as website,
        metadata->>'projectTwitter' as project_twitter,
        metadata->>'projectGithub' as project_github,
        metadata->>'userGithub' as user_github,
        metadata->>'logoImg' as logo_image,
        metadata->>'bannerImg' as banner_image,
        cast(metadata->>'createdAt' as numeric) as created_at,
        metadataCid as metadata_cid,
        name as name,
        nodeId as node_id,
        nonce,
        projectNumber as project_number,
        projectType as project_type,
        registryAddress as registry_address,
        tags,
        updatedAtBlock as updated_at_block
    from source
)

select * from renamed
