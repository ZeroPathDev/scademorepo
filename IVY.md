# Ivy applications

These Java applications use Ant for compilation and Ivy for dependency resolution.
They target Java 11 and can be built with JDK 11 or later, Ant 1.10 and Ivy 2.5.3.
Pass the Ivy JAR to Ant with `-lib`, or install it in your Ant library directory.

| Application | Responsibility | Libraries |
| --- | --- | --- |
| `collection-intake` | Turns approved invoice batches into payment intake files. | Commons CSV parses incoming files, Commons Collections selects ready invoices, and Commons Text formats payment lines. Commons Lang arrives through Commons Text. |
| `profile-import` | Normalizes customer profile exports for the customer directory. | Commons CSV handles quoted fields and Commons BeanUtils binds supported columns. BeanUtils brings in Commons Collections and Commons Logging. |
| `notification-renderer` | Renders notification templates using recipient properties. | The internal template client brings in Commons Text and Commons Lang through the local Ivy repository. |

Build an application from the repository root:

```sh
ant -lib /opt/ivy/ivy-2.5.3.jar -f collection-intake/build.xml
ant -lib /opt/ivy/ivy-2.5.3.jar -f profile-import/build.xml
ant -lib /opt/ivy/ivy-2.5.3.jar -f notification-renderer/build.xml
```

Each application writes its JAR and runtime libraries under its own `build/`
directory. `build-support/ivy-java.xml` contains the shared compile and package
targets. Application dependencies belong to the `runtime` configuration, which
maps to each dependency's `default` configuration.

The notification renderer keeps the template client's source and Ivy publication
descriptor together. Its build first packages the client into the local repository,
then resolves and compiles the application. `ivysettings.xml` loads the repository
chain from `repositories.xml`; `versions.properties` selects the client release.
The chain checks the local repository before Maven Central.

See each application's README for input formats and launch commands.
