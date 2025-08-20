with 

source as (

    select * from {{ ref('src_constructor_results') }}

),

renamed as (

    select
        constructorresultsid,
        raceid,
        constructorid,
        points,
        status

    from source

)

select * from renamed
