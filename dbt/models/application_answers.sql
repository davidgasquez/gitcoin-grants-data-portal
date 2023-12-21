with  source as (
        select metadata, chainid, roundid, projectid, id from {{ source("public", "raw_round_applications") }}
    ),

    renamed as (
        select
            unnest(
                from_json(json_extract_path_text(source.metadata, '$.application.answers'), '["json"]')
            ) as row_json,
            chainid as chain_id,
            roundid as round_id,
            id as application_id,
            projectid as project_id
        from source
    ),

    extracted as (
        select
            json_extract_path_text(row_json, 'questionId') as question_id,
            project_id,
            application_id,
            chain_id,
            lower(round_id) as round_id,
            json_extract_path_text(row_json, 'question') as question,
            json_extract_path_text(row_json, 'type') as question_type,
            json_extract_path_text(row_json, 'answer') as answer
        from renamed
    )

select * from extracted where answer is not null  -- filters out encrypted and skipped answers
