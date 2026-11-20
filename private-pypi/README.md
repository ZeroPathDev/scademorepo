# private-pypi

This app imports a real private package whose source is in `../registry-fixtures/packages`.
That package also requires a public dependency. Follow [REGISTRY_REHEARSAL.md](../REGISTRY_REHEARSAL.md)
to publish it, configure an authenticated mirror or cloud connection, and verify
both packages. It intentionally starts without a generated lockfile.
