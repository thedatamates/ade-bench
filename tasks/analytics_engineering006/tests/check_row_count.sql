with fact_inventory__solution as (
    select count(*) as row_count from solution__fact_inventory
),

fact_inventory__test as (
    select count(*) as row_count from fact_inventory
),

combined as (
    select
        count(*) as matches
    from fact_inventory__solution s
    join fact_inventory__test t
        on t.row_count = s.row_count
    where s.row_count > 0
)

select * from combined where matches != 1