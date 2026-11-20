# Ivy paths with spaces and Unicode

The application path and settings path contain spaces and Unicode. The settings
include uses an encoded space. Resolution must load `public sources.xml` once and
return `commons-collections:commons-collections:3.2.1`, without scanning a sibling
application's settings.

Build from the repository root with JDK 11+, Ant and Ivy 2.5.3:

```sh
ant -lib /opt/ivy/ivy-2.5.3.jar -f 'ivy paths ünicode/build.xml'
```
