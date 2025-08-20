with 

source as (

    select * from {{ ref('src_driver_standings') }}

),

renamed as (

    select
        driverstandingsid,
        raceid,
        driverid,
        points,
        position,
        positiontext,
        wins

    from source

)

select * from renamed
