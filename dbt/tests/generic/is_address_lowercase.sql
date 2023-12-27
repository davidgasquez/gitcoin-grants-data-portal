{% test is_address_lowercase(model, column_name) %}

select *
    from {{ model }}
    where {{ column_name }} is not null
    and {{ column_name }} != lower({{ column_name }})

{% endtest %}