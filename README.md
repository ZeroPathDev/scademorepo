Shared internal services and tooling across multiple languages and runtimes.

The following SCA fixtures provide a vulnerable and a clean example for each customer ecosystem. Every example includes direct and transitive dependencies.

| Ecosystem | Vulnerable example | Clean example |
| --- | --- | --- |
| Java / Maven | [maven-vulnerable](maven-vulnerable) | [maven-clean](maven-clean) |
| JavaScript / npm | [npm-vulnerable](npm-vulnerable) | [npm-clean](npm-clean) |
| Python / PyPI | [pypi-vulnerable](pypi-vulnerable) | [pypi-clean](pypi-clean) |
| C/C++ / Conan 2 | [cpp-vulnerable](cpp-vulnerable) | [cpp-clean](cpp-clean) |

Each vulnerable example has at least two distinct vulnerable packages. The clean examples have no known vulnerable packages in their resolved application dependency trees as checked on **2026-09-10**. See [SCA-EXAMPLES.md](SCA-EXAMPLES.md) for dependency paths, advisory references, build commands, and audit instructions.
