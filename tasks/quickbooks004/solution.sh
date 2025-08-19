#!/bin/bash
## Files to update
double_entry_transactions_files=(
  int_quickbooks__bill_double_entry.sql
  int_quickbooks__bill_payment_double_entry.sql
  int_quickbooks__credit_memo_double_entry.sql
  int_quickbooks__invoice_double_entry.sql
  int_quickbooks__journal_entry_double_entry.sql
  int_quickbooks__payment_double_entry.sql
  int_quickbooks__purchase_double_entry.sql
  int_quickbooks__refund_receipt_double_entry.sql
  int_quickbooks__sales_receipt_double_entry.sql
  int_quickbooks__vendor_credit_double_entry.sql
)

intermediate_files=(
  int_quickbooks__bill_join.sql
  int_quickbooks__expenses_union.sql
  int_quickbooks__invoice_join.sql
  int_quickbooks__sales_union.sql
)

transaction_lines_files=(
  int_quickbooks__bill_transactions.sql
  int_quickbooks__credit_memo_transactions.sql
  int_quickbooks__deposit_transactions.sql
  int_quickbooks__invoice_transactions.sql
  int_quickbooks__journal_entry_transactions.sql
  int_quickbooks__purchase_transactions.sql
  int_quickbooks__refund_receipt_transactions.sql
  int_quickbooks__sales_receipt_transactions.sql
  int_quickbooks__vendor_credit_transactions.sql
)

ap_ar="quickbooks__ap_ar_enhanced.sql"
dbt_yml="dbt_project.yml" 

## Solutions directory
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

for file in "${double_entry_transactions_files[@]}"; do
  cp $SOLUTIONS_DIR/$file models/double_entry_transactions/$file
done

for file in "${intermediate_files[@]}"; do
  cp $SOLUTIONS_DIR/$file models/intermediate/$file
done

for file in "${transaction_lines_files[@]}"; do
  cp $SOLUTIONS_DIR/$file models/transaction_lines/$file
done

cp $SOLUTIONS_DIR/$ap_ar models/$ap_ar
cp $SOLUTIONS_DIR/$dbt_yml $dbt_yml

dbt run