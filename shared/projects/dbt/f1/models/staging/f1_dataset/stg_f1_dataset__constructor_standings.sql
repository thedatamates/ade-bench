with 

source as (

    select * from {{ ref('src_constructor_standings') }}

),

renamed as (

    select
        constructorstandingsid,
        raceid,
        constructorid,
        points,
        position,
        positiontext,
        wins

    from source

)

select * from renamed
