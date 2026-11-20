Shared internal services and tooling across multiple languages and runtimes.

The collection intake, profile import and notification rendering applications
use Ant and Ivy. See [Ivy applications](IVY.md) for their build and runtime setup.

The Ivy and `private-*` applications cover public/internal registry resolution,
including repositories without settings and incomplete graphs. Follow
[the private package and mirror rehearsal](REGISTRY_REHEARSAL.md) to build real
fixtures, qualify authenticated mirrors, and check full/PR inventory and findings.
