{{ config(enabled=var('asana__using_tags', True)) }}

select * 
from {{ var('tag') }}