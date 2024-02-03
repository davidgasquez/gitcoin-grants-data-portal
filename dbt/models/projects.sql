with source as (
      select * from {{ source('public', 'raw_projects') }}
),

renamed as (
    select
        {{ adapter.quote("id") }} as project_id,
        {{ adapter.quote("projectNumber") }} as project_number,
        {{ adapter.quote("metaPtr") }} as meta_ptr,
        {{ adapter.quote("metadata") }} as metadata,
        {{ adapter.quote("owners") }} as owners,
        {{ adapter.quote("createdAtBlock") }} as created_at_block,
        {{ adapter.quote("chainId") }} as chain_id
    from source
),

extracted_metadata as (
    select
        *,
        json_extract_path_text(metadata, 'title') as title,
        json_extract_path_text(metadata, 'description') as description,
        json_extract_path_text(metadata, 'website') as website,
        json_extract_path_text(metadata, 'projectTwitter') as project_twitter,
        json_extract_path_text(metadata, 'projectGithub') as project_github,
        json_extract_path_text(metadata, 'userGithub') as user_github,
        json_extract_path_text(metadata, 'logoImg') as logo_image,
        json_extract_path_text(metadata, 'bannerImg') as banner_image,
        json_extract_path_text(metadata, 'createdAt')::numeric as created_at,
    from renamed
)

select * from extracted_metadata
