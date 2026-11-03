# Notification renderer

Renders a UTF-8 notification template with values from a recipient properties
file. Templates refer to fields such as `${customerName}`, `${invoiceId}` and
`${amount}`. Missing fields stop rendering; recipient values are inserted as
literal text.

The renderer uses the internal `template-client` library. Its source lives in
`client/src/main/java`, and its publication descriptor is in the local Ivy
repository. Ant packages the client before resolving the application's libraries.
The selected client version is maintained in `versions.properties`.

After building with Ant, run from this directory:

```sh
java -cp 'build/notification-renderer.jar:build/lib/*' \
  com.northbeam.templates.TemplateService templates/payment-reminder.txt recipient.properties
```
