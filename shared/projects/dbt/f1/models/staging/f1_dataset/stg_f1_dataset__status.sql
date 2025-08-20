with 

source as (

    select * from {{ ref('src_status') }}

),

renamed as (

    select
        statusid,
        status

    from source

)

select * from renamed
