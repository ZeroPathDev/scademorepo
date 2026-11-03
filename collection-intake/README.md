# Collection intake

Converts invoice exports into tab-separated payment intake files. Only invoices
with status `ready` and a positive amount are included. Rows are processed in
batches of 500 so larger exports do not need to fit in memory.

The input CSV requires `invoiceId`, `customerId`, `amount` and `status` headers.
Identifiers may contain letters, numbers, underscores and hyphens. The output
contains invoice ID, customer ID and amount, without a header.

After building with Ant, run from this directory:

```sh
java -cp 'build/collection-intake.jar:build/lib/*' \
  com.northbeam.collections.CollectionIntake invoices.csv payments.tsv
```
