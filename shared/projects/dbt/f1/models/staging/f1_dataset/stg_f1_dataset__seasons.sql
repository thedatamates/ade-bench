with 

source as (

    select * from {{ ref('src_seasons') }}

),

renamed as (

    select
        year,
        url

    from source

)

select * from renamed
