# Private package and mirror rehearsal

Use this corpus with the Cunningham Ivy/private-registry PR. Pin both source SHAs
in the rehearsal record. A successful public-only scan is not sufficient.

The private fixtures contain small, real packages with public dependencies. They
are not published to any public registry. The fixture account must be denied
anonymous access and have read access for scanning. Publishing uses a separate
account. Keep credentials out of the repository and evidence files.

## Ivy scenarios

| App | Expected behavior |
| --- | --- |
| `ivy-public-default` | Resolve public packages without any settings file. |
| `ivy-ant-declarations` | Read top-level Ant properties and settings without running targets. |
| `ivy-private-maven` | Resolve an internal Maven-layout package through the configured Nexus group, without settings. |
| `ivy-private-fallback` | Try a saved Maven connection after Central-only project settings. |
| `ivy-private-native` | Use a saved native Ivy connection; the private descriptor has no POM. |
| `ivy-private-native-mirror` | Rewrite an explicitly declared Ivy layout through operator mirrors and use the operator Secret. |
| `ivy-partial-resolution` | Keep the public package, report the missing private package, mark coverage incomplete. |
| `ivy paths ünicode` | Read settings with spaces, Unicode and an encoded local include; keep sibling settings isolated. |

`registry-fixtures/expected-ivy-inventory.json` defines the required resolved
packages. Full inventory and findings-only inventory must both preserve incomplete
resolution metadata. Run a full scan with SAST disabled and SCA enabled too.
Compare the minimum dependency edges with persisted inventory and exported SBOMs.
Every incomplete entry requires a nonempty manifest-level coverage warning.

## Publish and connect

Build the Java fixtures locally (JDK 11+):

```sh
python3 registry-fixtures/publish.py --output /tmp/rehearsal-packages
```

To publish, set `REHEARSAL_MAVEN_URL` to a hosted Maven repository and
`REHEARSAL_IVY_URL` to a hosted raw/Ivy repository, then set
`REHEARSAL_REGISTRY_USERNAME` and `REHEARSAL_REGISTRY_PASSWORD`. Run the same
command with `--publish`. It verifies authenticated downloads and anonymous denial.
The script refuses HTTP and redirects. It must fail for missing credentials.

The `private-npm`, `private-pypi`, `private-cargo`, `private-rubygems`,
`private-composer`, `private-nuget` and `private-go` apps exercise the corresponding
native protocols. `private-sbt` additionally checks cold launcher boot and
Maven-layout private dependencies. Their real private package sources are in
`registry-fixtures/packages`. Build archives and metadata with Python and RubyGems:

```sh
python3 registry-fixtures/build_packages.py --output /tmp/private-packages \
  --base-url https://registry.rehearsal.example/repository/fixtures
```

Publish archives to hosted repositories using the native clients (npm publish,
twine upload, cargo publish, gem nexus, dotnet nuget push). Use Nexus groups that
include these hosted packages and the public proxy. Serve Composer's generated
repository and Go's generated module-proxy files through authenticated HTTPS,
with public package proxying configured. A static directory containing only the
private fixtures cannot resolve their public transitives.

After publishing, prove that anonymous private reads are denied. Test the account
with each ecosystem's private metadata path before saving cloud connections.

## Run native qualification in the rehearsal workload

Place this exact committed corpus in the SCA worker's shared scan storage, then
run inside the SCA image with its normal service account, environment and volumes:

```sh
python -m lib.sca.resolver_preflight --private-corpus /mnt/scanstorage/scademorepo
```

This creates the real resolver pod and checks both the private direct dependency
and its public transitive for every entry in `registry-fixtures/native-canaries.json`.
Missing credentials, source files, tools, packages or incomplete Ivy coverage fail.
It also verifies resolver RPC authentication, snapshot access and pod cleanup.
Run the ordinary Helm public-package preflights as well. The native qualification
does not replace the full/PR scan and finding-lifecycle checks below.
Repeat with the rehearsal's private CA and blocked public egress. The group must
serve public dependencies itself; an unrestricted workstation is not sufficient
evidence that the deployed mirror works. Also test anonymous public-only groups
and private-only repositories paired with the appropriate public proxy.

For on premises, include the hosted Maven repository and Maven Central proxy in
the existing Nexus Maven group. Set `sca.registries.maven` to that group and
`sca.registryCredentialsSecret` to the read-only account's Secret. Do not add an
organization Maven connection for this scenario: it must work from mirror settings.

For native Ivy, configure `sca.sandbox.ivyMirrors` with source
`https://ivy.rehearsal.invalid/native`, the hosted Ivy repository as `mirror`, and
`com.zeropath.rehearsal/native-policy/1.0.0/ivy.xml` as `probe`. The Secret's scope
must cover the final mirror repository URL. Run `ivy-private-native-mirror`.

For cloud, connect the group as Maven and separately connect the hosted raw
repository as Ivy. Validate the same private descriptor and use pattern
`[organisation]/[module]/[revision]/ivy.xml`. Run `ivy-private-native`, which has
no settings file. Also exercise connect, credential rotation, failed rotation,
removal and tenant isolation.

## Required negative checks

1. Replace the read password with a wrong value: the preflight and private
   resolution must fail visibly. Restore it and confirm recovery.
2. Remove the internal package while retaining public access: public inventory
   must survive and the affected manifest must remain incomplete.
3. Start from a scan with a known vulnerable public transitive. Break private
   resolution and rescan: the previous finding must stay open.
4. Change only Ant properties in a PR. Head and base must use their committed
   values, not a dirty working tree. A partial head/base must make the review
   incomplete and cannot prove remediation.
5. Include two organizations with different credentials on the same registry
   host. Neither scan may use the other's account, paths or cached metadata.

Keep scan IDs, fixture/source SHAs, manifest-level inventory, dependency edges,
coverage warnings and finding state transitions in the rehearsal evidence. Do not
record credentials or claim a pass from a preflight alone.

## Existing lockfile-only ecosystems

`private-conan` and `private-cocoapods` contain real internal package source and
native-generated lockfiles with public dependencies. Their READMEs explain how
to regenerate them and the extra steps for remote private publication. These
examples qualify committed inventory, not managed registry connections. Conan,
CocoaPods, Dart and Hex do not currently have native resolver runtimes in
ZeroPath; a manifest without a committed lockfile does not gain resolution from
these changes. Private Git sources retain the existing VCS authentication path.

## Local fixture checks

With Python, JDK 11+ and RubyGems installed, run:

```sh
python3 -m unittest discover -s registry-fixtures -p 'test_*.py' -v
```

CI builds these fixtures without publishing. Cunningham also runs real native
clients against the archives over authenticated HTTPS with correct and incorrect
credentials. Its opt-in corpus test requires `SCA_PRIVATE_CORPUS` to name this
checkout and native clients on PATH. These checks do not replace live Nexus
qualification.
