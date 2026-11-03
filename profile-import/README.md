# Profile import

Normalizes customer profile exports before they are loaded into the customer
directory. The importer trims fields, binds the supported columns to the profile
model and checks the customer ID, email and display name before writing a row.
Extra source columns are ignored.

Input and output use the CSV headers `customerId`, `email`, `displayName` and
`department`. Quoted commas and line breaks are preserved.

After building with Ant, run from this directory:

```sh
java -cp 'build/profile-import.jar:build/lib/*' \
  com.northbeam.profiles.ProfileImport source.csv normalized.csv
```
