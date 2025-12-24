#!/bin/bash

## Introduce an error by changing the data type of the underlying table.

## Get the schema based on the database type.
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema='main'
else
    schema='public'
fi

# Execute SQL using the run_sql utility.
/scripts/run_sql.sh "$@" << SQL
create or replace table ${schema}.refund_receipt_data_temp as
  select * replace (transaction_date::date as transaction_date)
  from ${schema}.refund_receipt_data;

create or replace table ${schema}.sales_receipt_data_temp as
  select * replace (transaction_date::date as transaction_date)
  from ${schema}.sales_receipt_data;

create or replace table ${schema}.estimate_data_temp as
  select * replace (due_date::date as due_date)
  from ${schema}.estimate_data;

drop table ${schema}.sales_receipt_data;
drop table ${schema}.refund_receipt_data;
drop table ${schema}.estimate_data;

alter table ${schema}.sales_receipt_data_temp rename to sales_receipt_data;
alter table ${schema}.refund_receipt_data_temp rename to refund_receipt_data;
alter table ${schema}.estimate_data_temp rename to estimate_data;
SQL