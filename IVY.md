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

## Scanning with ZeroPath

`collection-intake` and `profile-import` intentionally have no `ivysettings.xml`.
ZeroPath resolves their public packages through Maven Central, or the deployment's
Maven mirror. If the organization has a saved Maven registry connection, that
connection supplies the default repository for a manifest without settings. Use
a Nexus group that includes both private packages and the public proxy.

The expected inventories are four packages for `collection-intake`, four for
`profile-import`, and three for `notification-renderer`. These were verified on
2026-11-20 against public Maven Central and the on-premise rehearsal's Nexus.
The notification example uses a repository-local private descriptor; it does not
by itself test authentication to a remote registry.

The fixes on Cunningham's `fix/ivy-private-registry-coverage` branch add a saved
Maven connection as a fallback after project settings. A Nexus Maven group can
therefore supply internal packages and public transitives without a second
connection or a new `ivysettings.xml`. An explicitly declared repository also
works, for example:

```xml
<ivysettings>
  <settings defaultResolver="company"/>
  <resolvers>
    <ibiblio name="company" m2compatible="true"
             root="https://nexus.example.com/repository/maven-all/"/>
  </resolvers>
</ivysettings>
```

Keep credentials in ZeroPath's registry connection. For a native Ivy layout,
declare its descriptor pattern with a URL resolver; a Maven mirror cannot infer
that layout. On premises, `sca.sandbox.ivyMirrors` can map that resolver's source
prefix to Nexus while preserving its pattern. Credentials must match the final
mirror URL. The descriptor preflight uses the same operator Secret as scans.

ZeroPath reads settings beside each `ivy.xml` and reads top-level Ant property,
property-file, import/include and Ivy settings declarations. It does not execute
Ant targets. Projects can also load properties from settings directly:

```xml
<ivysettings>
  <properties file="${ivy.settings.dir}/build.properties"/>
  <include file="${ivy.settings.dir}/ivy/ivysettings.xml"/>
</ivysettings>
```

An unresolved dependency retains the packages Ivy successfully resolved and marks
the manifest incomplete. That partial result cannot prove an old finding fixed.
PR scans resolve both committed revisions, including property-only changes.

These are expected behaviors for the proposed fix, not a claim that an older
published on-premises release has them. See [REGISTRY_REHEARSAL.md](REGISTRY_REHEARSAL.md)
for authenticated fixtures and acceptance checks.
